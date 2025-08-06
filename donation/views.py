from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.utils import phone_number_required
import razorpay
from django.template.loader import render_to_string
# from notifications.utils.email_utils import send_emails
from .models import PaymentGateway, Payments, Donation, Registration_fee
from .forms import DonationForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages


def donate(request):
    context = {
    }
    return render(request, 'donation/donate.html', context)

@login_required
@phone_number_required
def complete_registration(request):
    if request.user.registration_fee_paid:
        return redirect('/dashboard/')
    
    context = {
    }
    return render(request, 'donation/complete-registration.html', context)

# Registration Payment Setup
@login_required
@phone_number_required
def registration_proceed_payment(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount < 1:
                messages.warning(request, "Registration fees amount can't be below 1 Rupees.")
                return redirect('/donate/complete-registration/')

            gateway = PaymentGateway.objects.first()
            if not gateway:
                messages.error(request, "Payment gateway not configured.")
                return redirect('/donate/complete-registration/')

            currency = 'INR'

            # Create RazorPay client
            client = razorpay.Client(auth=(gateway.razorpay_id, gateway.razorpay_secret))

            # Create a RazorPay order
            try:
                razorpay_order = client.order.create({
                    'amount': int(amount * 100),  # Amount in paise
                    'currency': currency,
                    'receipt': f'Thanks for your support of {amount} Rs.',
                    'payment_capture': '1'
                })

                paymentobj = Payments.objects.create(user=request.user, 
                                                     razorpay_order_id=razorpay_order['id'],
                                                     payment_method='RAZORPAY', 
                                                     amount_paid=amount, 
                                                     status='Pending')

                # Prepare context for the template
                context = {
                    'user': request.user,
                    'order_id': razorpay_order['id'],
                    'razorpay_key_id': gateway.razorpay_id,
                    'amount': amount,
                    'currency': currency,
                    'name': request.user.first_name,
                    'email': request.user.email,
                    'contact': request.user.phone_number,
                    'callback_url': f"{request.scheme}://{request.get_host()}/donate/register/razorpay_callback/",
                }
                return render(request, 'payment/registration_razorpay_payment.html', context)

            except Exception as e:
                messages.error(request, f"Error creating Razorpay order: {str(e)}")
                return redirect('/donate/complete-registration/')

        else:
            messages.warning(request, "Invalid donation form.")
            return redirect('/donate/complete-registration/')

    return redirect('/donate/complete-registration/')

# Registration Payment Setup
@login_required
def registration_razorpay_callback(request):
    payment_id = request.GET.get('razorpay_payment_id')
    order_id = request.GET.get('razorpay_order_id')
    signature = request.GET.get('razorpay_signature')
    error = request.GET.get('error')

    if not order_id:
        messages.error(request, 'Payment Failed during callback!')
        return redirect('razorpay_failure')

    try:
        gateway = PaymentGateway.objects.first()
        if not gateway:
            messages.error(request, 'Payment gateway not configured')
            raise Exception("Payment gateway not configured")

        if error == 'payment_failed':
            try:
                # Get the most recent unprocessed order for this user with matching payment ID
                payment = Payments.objects.filter(
                    razorpay_order_id=order_id,
                    user=request.user,
                    status='Pending'
                ).latest('created_at')

                payment.status = 'Failed'
                payment.save()
                messages.error(request, 'Payment gateway not configured')
                return redirect('razorpay_failure')

            except Payments.DoesNotExist:
                return redirect('razorpay_failure')

        # Verify the payment signature
        client = razorpay.Client(auth=(gateway.razorpay_id, gateway.razorpay_secret))
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # Payment successful, update order and payment
            try:
                payment = Payments.objects.get(razorpay_order_id=order_id)

                if payment.status == 'Pending':
                    payment.status = 'Success'
                    payment.razorpay_payment_id = payment_id
                    payment.razorpay_signature = signature
                    payment.save()

                    # Send confirmation email
                    try:
                        variables = {
                            'payment': payment,
                            'request': request,
                        }
                        message = render_to_string('emails/registration-confirmation.html', variables)
                        # send_emails('Donation Successful', message, [payment.user.email], message)
                    except Exception as e:
                        print(f'Error sending email: {e}')

                    return redirect('razorpay_success')

                else:
                    return redirect('razorpay_failure')

            except Payments.DoesNotExist:
                return redirect('razorpay_failure')

        except razorpay.errors.SignatureVerificationError:
            # Handle invalid signature
            return redirect('razorpay_failure')

    except Exception as e:
        # Log the error for debugging
        print(f"Error in razorpay_callback: {str(e)}")
        return redirect('razorpay_failure')


# Registration Payment Setup
@csrf_exempt
def registration_razorpay_success(request):
    try:
        razorpay_payment_id = request.GET.get('razorpay_payment_id')
        razorpay_order_id = request.GET.get('razorpay_order_id')
        razorpay_signature = request.GET.get('razorpay_signature')

        # Find the payment record (using order_id as that's what we stored)
        payment = Payments.objects.filter(razorpay_order_id=razorpay_order_id).first()

        if payment:
            payment.status = 'Successful'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()
            Registration_fee.objects.create(user=request.user, amount=payment.amount_paid)

            try:
                variables = {
                    'payment': payment,
                    'request': request,
                }
                message = render_to_string('emails/registration-confirmation.html', variables)
                # send_emails('Donation Successful', message, [payment.user.email], message)
            except Exception as e:
                print(f'Error sending email: {e}')

            amount = float(payment.amount_paid)
            trees_planted = round(amount / 100, 2)    
            co2_absorbed = round(trees_planted * 20, 1)
            oxygen_produced = round(trees_planted * 118, 1)
            jobs_created = round(amount / 5000, 1)

            context = {
                'amount': payment.amount_paid,
                'transaction_id': payment.razorpay_payment_id,
                'trees_planted': trees_planted,
                'co2_absorbed': co2_absorbed,
                'oxygen_produced': oxygen_produced,
                'jobs_created': jobs_created,
            }
            return render(request, 'donation/registration-completed.html', context)
        else:
            messages.error(request, 'Payment Failed!')
            return redirect('razorpay_failure')
    except Exception as e:
        messages.error(request, 'Payment Failed!')
        print(f'RazorPay success error: {e}')
        return redirect('razorpay_failure')

# Registration Payment Setup
@csrf_exempt
def registration_razorpay_failure(request):
    try:
        messages.error(request, 'Payment Failed!')
        razorpay_order_id = request.GET.get('razorpay_order_id')
        # Find the payment record
        payment = Payments.objects.filter(razorpay_order_id=razorpay_order_id).first()

        if payment:
            payment.status = 'Failed'
            payment.save()
            messages.error(request, f'Payment failed for Registration {razorpay_order_id}.')

    except Exception as e:
        messages.error(request, 'Payment Failed!')
        print(f'RazorPay failure error: {e}')

    return redirect("/donate/complete-registration/")



# -=-=-=-=-= Donation Payment Setup -=-=-=-=-=-=-
@login_required
@phone_number_required
def proceed_payment(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if amount < 1:
                messages.warning(request, "Donation amount can't be below 1 Rupees.")
                return redirect('/donate/')

            gateway = PaymentGateway.objects.first()
            if not gateway:
                messages.error(request, "Payment gateway not configured.")
                return redirect('/donate/')

            currency = 'INR'

            # Create RazorPay client
            client = razorpay.Client(auth=(gateway.razorpay_id, gateway.razorpay_secret))

            # Create a RazorPay order
            try:
                razorpay_order = client.order.create({
                    'amount': int(amount * 100),  # Amount in paise
                    'currency': currency,
                    'receipt': f'Thanks for your support of {amount} Rs.',
                    'payment_capture': '1'
                })

                paymentobj = Payments.objects.create(user=request.user, 
                                                     razorpay_order_id=razorpay_order['id'],
                                                     payment_method='RAZORPAY', 
                                                     amount_paid=amount, 
                                                     status='Pending')

                # Prepare context for the template
                context = {
                    'user': request.user,
                    'order_id': razorpay_order['id'],
                    'razorpay_key_id': gateway.razorpay_id,
                    'amount': amount,
                    'currency': currency,
                    'name': request.user.first_name,
                    'email': request.user.email,
                    'contact': request.user.phone_number,
                    'callback_url': f"{request.scheme}://{request.get_host()}/donate/razorpay_callback/",
                }
                return render(request, 'payment/razorpay_payment.html', context)

            except Exception as e:
                messages.error(request, f"Error creating Razorpay order: {str(e)}")
                return redirect('/donate/')

        else:
            messages.warning(request, "Invalid donation form.")
            return redirect('/donate/')

    return redirect('/donate/')


@login_required
def razorpay_callback(request):
    payment_id = request.GET.get('razorpay_payment_id')
    order_id = request.GET.get('razorpay_order_id')
    signature = request.GET.get('razorpay_signature')
    error = request.GET.get('error')

    if not order_id:
        messages.error(request, 'Payment Failed!')
        return redirect('razorpay_failure')

    try:
        gateway = PaymentGateway.objects.first()
        if not gateway:
            messages.error(request, 'Payment gateway not configured')
            raise Exception("Payment gateway not configured")

        if error == 'payment_failed':
            try:
                # Get the most recent unprocessed order for this user with matching payment ID
                payment = Payments.objects.filter(
                    razorpay_order_id=order_id,
                    user=request.user,
                    status='Pending'
                ).latest('created_at')

                payment.status = 'Failed'
                payment.save()
                messages.error(request, 'Payment gateway not configured')
                return redirect('razorpay_failure')

            except Payments.DoesNotExist:
                return redirect('razorpay_failure')

        # Verify the payment signature
        client = razorpay.Client(auth=(gateway.razorpay_id, gateway.razorpay_secret))
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            # Payment successful, update order and payment
            try:
                payment = Payments.objects.get(razorpay_order_id=order_id)

                if payment.status == 'Pending':
                    payment.status = 'Success'
                    payment.razorpay_payment_id = payment_id
                    payment.razorpay_signature = signature
                    payment.save()

                    # Send confirmation email
                    try:
                        variables = {
                            'payment': payment,
                            'request': request,
                        }
                        message = render_to_string('emails/donation-confirmation.html', variables)
                        # send_emails('Donation Successful', message, [payment.user.email], message)
                    except Exception as e:
                        print(f'Error sending email: {e}')

                    return redirect('razorpay_success')

                else:
                    return redirect('razorpay_failure')

            except Payments.DoesNotExist:
                return redirect('razorpay_failure')

        except razorpay.errors.SignatureVerificationError:
            # Handle invalid signature
            return redirect('razorpay_failure')

    except Exception as e:
        # Log the error for debugging
        print(f"Error in razorpay_callback: {str(e)}")
        return redirect('razorpay_failure')


@csrf_exempt
def razorpay_success(request):
    try:
        razorpay_payment_id = request.GET.get('razorpay_payment_id')
        razorpay_order_id = request.GET.get('razorpay_order_id')
        razorpay_signature = request.GET.get('razorpay_signature')

        # Find the payment record (using order_id as that's what we stored)
        payment = Payments.objects.filter(razorpay_order_id=razorpay_order_id).first()

        if payment:
            payment.status = 'Successful'
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.save()
            Donation.objects.create(user=request.user, amount=payment.amount_paid)

            try:
                variables = {
                    'payment': payment,
                    'request': request,
                }
                message = render_to_string('emails/donation-confirmation.html', variables)
                # send_emails('Donation Successful', message, [payment.user.email], message)
            except Exception as e:
                print(f'Error sending email: {e}')

            amount = float(payment.amount_paid)
            trees_planted = round(amount / 100, 2)    
            co2_absorbed = round(trees_planted * 20, 1)
            oxygen_produced = round(trees_planted * 118, 1)
            jobs_created = round(amount / 5000, 1)

            context = {
                'amount': payment.amount_paid,
                'transaction_id': payment.razorpay_payment_id,
                'trees_planted': trees_planted,
                'co2_absorbed': co2_absorbed,
                'oxygen_produced': oxygen_produced,
                'jobs_created': jobs_created,
            }
            return render(request, 'donation/donation-completed.html', context)
        else:
            messages.error(request, 'Payment Failed!')
            return redirect('razorpay_failure')
    except Exception as e:
        messages.error(request, 'Payment Failed!')
        print(f'RazorPay success error: {e}')
        return redirect('razorpay_failure')

@csrf_exempt
def razorpay_failure(request):
    try:
        messages.error(request, 'Payment Failed!')
        razorpay_order_id = request.GET.get('razorpay_order_id')
        # Find the payment record
        payment = Payments.objects.filter(razorpay_order_id=razorpay_order_id).first()

        if payment:
            payment.status = 'Failed'
            payment.save()
            messages.error(request, f'Payment failed for Donation {razorpay_order_id}.')

    except Exception as e:
        messages.error(request, 'Payment Failed!')
        print(f'RazorPay failure error: {e}')

    return redirect("/donate/")
