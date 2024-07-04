from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
import google.generativeai as genai
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

# Set your Google Generative AI API key
key = "AIzaSyB2Ap-o973pkpyvPaKiktbZwd4LX1FxU2c"
genai.configure(api_key=key)

convo=("""**bot:** Hello, thank you for contacting us. How can I assist you today?

**User:** I bought a MacBook Air M2 from you and it's defective! I want a replacement now!

**bot:** I'm truly sorry to hear about the issue with your MacBook Air M2. We understand your frustration. Could you please provide me with your order ID so I can look into this for you?

**User:** It's ORD12347! And don't waste my time, I need this sorted out ASAP.

**bot:** I completely understand your urgency, ORD12347. Let me check the status of your return request and expedite the replacement process for you. One moment, please.

**User:** It's been a hassle from the start. The laptop arrived late, and now it's defective! This is unacceptable!

**bot:** I apologize for the inconvenience caused, ORD12347. I can see that the MacBook Air M2 was returned. Let me confirm the replacement process and ensure it's expedited for you. Could you confirm your preferred delivery address for the replacement?

**User:** Just get it right this time! It should go to [User's Address].

**bot:** Thank you for confirming, ORD12347. I've updated the delivery details and expedited the replacement order. You will receive a confirmation email shortly with the new delivery date. Is there anything else I can assist you with today?

**User:** No, just make sure it arrives on time and is actually functional this time!

**bot:** Understood. We'll ensure everything is in order this time. If you have any further concerns, please don't hesitate to contact us. Thank you for your patience.

**User:** please connect me with live agent""")


@app.route('/')
def chatbot_index():
    return render_template('chatbot.html')


@app.route('/customer')
def customer_index():
    return render_template('customer.html')

@app.route('/agent')
def agent_index():
    return render_template('agent.html', summarized_text=summerize_text, department=department)




@socketio.on('message')
def handle_message(data):
    message = data['message']
    room = data['room']
    
    if data.get('from_agent'):
        emit('message', {'sender': 'Agent', 'message': message}, room=room)
    else:
        emit('message', {'sender': 'User', 'message': message}, room=room)
        
        if data.get('live_agent'):
            emit('message', {'sender': 'User', 'message': message}, room='agent_room')
        else:
            bot_message = qgen(message)
            

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    emit('message', {'sender': 'System', 'message': f'{data["username"]} has joined the room.'}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    emit('message', {'sender': 'System', 'message': f'{data["username"]} has left the room.'}, room=room)

prompt=f"""you are bot of ecomm company for customer support.the customer is wanted to chat with realtime agent because he is not satisfied
with your response . you will summerize the conversation between user and you. so that it will be very helpful for
real time agent to know about the cuatomer and no need ask that customer what his problem is.
the here is the converstion between you and customer{convo}. give clear instruction about this user to the live agent in very consise manner.give output under 3 lines.
"""


def qgen(userinput):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
    )
    response = model.generate_content(userinput)
    return response.text

summerize_text=qgen(prompt)

r_prompt=f"""Act as a customer issue routing manager. rout the user quaries to the proper department.
we have these departments in our comapnay.
(Customer Service/Support:

Handles general inquiries, order status, returns, and basic product information.
First point of contact for many customer issues.

Technical Support:

Manages issues related to website functionality, payment processing, account access, and technical glitches.
Assists customers with technical difficulties.

Billing and Payments:

Resolves issues related to payment processing, billing disputes, refunds, and invoice questions.
Ensures financial transactions are accurate and timely.

Shipping and Logistics:

Addresses concerns about delivery times, tracking orders, lost or damaged packages, and logistics queries.
Coordinates with shipping partners and warehouses.

Product and Inventory Management:

Deals with complaints about product quality, availability, discrepancies between product description and actual product, and stock issues.
Manages inventory levels and product catalog.

Returns and Refunds:

Specializes in handling returns, exchanges, and refunds.
Ensures a smooth return process and customer satisfaction.

Sales and Marketing:

Addresses issues related to promotions, discounts, loyalty programs, and marketing campaigns.
Handles queries about product recommendations and upselling.

Account Management:

Manages customer accounts, subscription services, and user profiles.
Handles issues related to account setup, security, and personalization.

Compliance and Legal:

Handles complaints related to privacy, terms of service, legal disputes, and compliance with regulations.
Ensures company policies align with legal standards.

Product Development and Quality Assurance:

Addresses feedback on product features, functionality, and quality.
Involves in improving products based on customer input.

Business Analytics and Insights:

Analyzes customer feedback for trends and insights.
Works on improving overall customer experience through data-driven decisions.

Partnerships and Vendor Management:

Manages issues related to third-party vendors, product suppliers, and service providers.
Ensures smooth collaboration with external partners.

Customer Experience and Loyalty:

Focuses on enhancing overall customer experience and building long-term loyalty.
Handles escalated complaints and works on customer retention strategies.

Fraud Prevention and Security:

Manages issues related to fraudulent activities, account security breaches, and transaction security.
Ensures safe and secure shopping experiences for customers.

Social Media and Public Relations:

Deals with complaints made via social media platforms and public forums.
Manages the company's reputation and customer communication on public channels.)

rout the user to a proper departmnet based on the basis of coversation history. just print department name dont add any additional comment
conversation={convo}
"""

department=qgen(r_prompt)

socketio.run(app, debug=True)
