from django.shortcuts import render, redirect
from management.models import JobOpening, Announcement
from dashboard.forms import JobApplicationForm, ContactFormForm

# Create your views here.
def index(request):
    context = {}
    return render(request, 'home/index.html',context)

def aboutus(request):
    context = {}
    return render(request, 'home/aboutus.html',context)

def privacy_policy(request):
    context = {}
    return render(request, 'home/privacy-policy.html',context)

def refund_policy(request):
    context = {}
    return render(request, 'home/refund-policy.html',context)

def terms_of_service(request):
    context = {}
    return render(request, 'home/terms-of-services.html',context)

def services(request):
    context = {}
    return render(request, 'home/services.html',context)

def testimonials(request):
    context = {}
    return render(request, 'home/testimonials.html',context)

def contactus(request):
    if request.method == 'POST':
        form = ContactFormForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'management/application-success.html')
        else:
            for e in form.errors:
                print(e)
    else:
        form = ContactFormForm()

    context = {}
    return render(request, 'home/contactus.html',context)

def careers(request):
    job_list = JobOpening.objects.all()
    form = JobApplicationForm()
    # Split requirements into lists for each job
    for job in job_list:
        job.requirements_list = job.requirements.split('\n')
    context = {
        'job_list': job_list,
        'form': form,
    }
    return render(request, 'home/careers.html',context)

def news(request):
    announcements = Announcement.objects.all()
    context = {
        'announcements': announcements,
    }
    return render(request, 'home/news.html',context)