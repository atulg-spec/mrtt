import requests
import sys
from donation.models import PaymentGateway

def create_upi_order(mobile_number, total_amount, order_id):
    gateway = PaymentGateway.objects.first()
    api_url = f"{gateway.gateway_url}/api/create-order"
    print(api_url)
    
    data = {
        "customer_mobile": mobile_number,
        "user_token": gateway.gateway_key,
        "amount": total_amount,
        "order_id": order_id,
        "redirect_url": f"http://127.0.0.1:8000/donate/upicallback/{order_id}/",
        "remark1": "A contribution",
        "remark2": 'For the future',
    }

    try:
        response = requests.post(api_url, data=data)
        response.raise_for_status()  # raises HTTPError for bad status codes
    except requests.RequestException as e:
        sys.exit(f"Request error: {e}")

    try:
        print(response.content)
        result = response.json()
    except ValueError:
        sys.exit("Invalid API response (not JSON)")

    if "status" in result:
        if result["status"] is True:
            payment_url = result["result"].get("payment_url")
            print(f"Redirect user to: {payment_url}")
            return payment_url
            # You could also open this in browser:
            # import webbrowser; webbrowser.open(payment_url)
        else:
            sys.exit(f"Payment Error: {result.get('message', 'Unknown error')}")
    else:
        sys.exit("Invalid API response structure")
