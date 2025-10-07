import requests
import time
import sys

def create_order(mobile_number, total_amount, order_id, vehicle_number):
    api_url = "https://payment.mrtt.org.in/api/create-order"
    
    data = {
        "customer_mobile": mobile_number,
        "user_token": "efd3ece659ad59f874505cfdc415d823",
        "amount": total_amount,
        "order_id": f"TAX{order_id}{int(time.time())}",
        "redirect_url": "https://payment.mrtt.org.in/api/create-order",
        "remark1": "Vehicle Tax Payment",
        "remark2": vehicle_number,
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
            # You could also open this in browser:
            # import webbrowser; webbrowser.open(payment_url)
        else:
            sys.exit(f"Payment Error: {result.get('message', 'Unknown error')}")
    else:
        sys.exit("Invalid API response structure")


# Example usage
if __name__ == "__main__":
    mobile_number = "9876543210"
    total_amount = "500"
    order_id = "12345"
    vehicle_number = "UP32AB1234"

    create_order(mobile_number, total_amount, order_id, vehicle_number)
