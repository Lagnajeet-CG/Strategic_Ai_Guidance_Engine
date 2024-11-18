import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import google.generativeai as genai
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Configure the OpenAI API
key = "AIzaSyB2Ap-o973pkpyvPaKiktbZwd4LX1FxU2c"
genai.configure(api_key=key)
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}
# Fetch the service account key from Streamlit secrets
service_account_info = st.secrets["GCP_SERVICE_ACCOUNT_KEY"]
credentials = service_account.Credentials.from_service_account_info(service_account_info)



# Set up BigQuery client
project_id = 'data-driven-cx'
client = bigquery.Client(credentials=credentials, project=project_id)

# Custom CSS for modern look and feel
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
        
        body {
            font-family: 'Roboto', sans-serif;
            color: #333333;
            background-color: #F0F2F6;
        }
        
        h1 {
            font-weight: bold;
            color: #1E90FF;
        }
        
        .sidebar .sidebar-content {
            background-color: #FFFFFF;
        }
        
        .stTextInput > div {
            background-color: #FFFFFF;
            border-radius: 5px;
            border: 1px solid #1E90FF;
            padding: 10px;
            margin-top: 10px;
        }
        
        button {
            background-color: #1E90FF;
            color: white;
            border-radius: 5px;
            border: none;
            padding: 10px 20px;
            transition: background-color 0.3s ease;
        }
        
        button:hover {
            background-color: #4682B4;
        }
        
        .stSlider {
            padding: 10px 0;
        }
        
        .stDataFrame {
            border-radius: 10px;
            box-shadow: 2px 2px 12px rgba(0, 0, 0, 0.1);
        }
        
        .card {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* Dark mode styles */
        .dark-mode {
            color: #F0F2F6;
            background-color: #1E1E1E;
        }
        
        .dark-mode .sidebar .sidebar-content {
            background-color: #2D2D2D;
        }
        
        .dark-mode .stTextInput > div {
            background-color: #2D2D2D;
            border-color: #4682B4;
        }
        
        .dark-mode .card {
            background-color: #2D2D2D;
        }
    </style>
""", unsafe_allow_html=True)

# App title and description
st.markdown('<h1>Strategic AI Guidance Engine🤖</h1>', unsafe_allow_html=True)

# # Path to your logo
logo_path2 = "gcp+capg+ikea_azure.png"

# Display the logo in the sidebar
st.sidebar.image(logo_path2,use_container_width=True)
# st.sidebar.title('SAGE')

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# User input via chat input
user_input = st.chat_input("Ask a question about the data...")





# Set your project ID and dataset ID
project_id = "data-driven-cx"
dataset_id = "EDW_ECOM"

# Function to fetch table schemas
def fetch_table_schemas(project_id, dataset_id):
    dataset_ref = client.dataset(dataset_id)
    tables = client.list_tables(dataset_ref)

    all_schemas_info = ""
    for table in tables:
        table_ref = dataset_ref.table(table.table_id)
        try:
            table = client.get_table(table_ref)
            schema_str = f"Schema for table {table.table_id}:\n"
            for field in table.schema:
                schema_str += f"  {field.name} ({field.field_type})\n"
            all_schemas_info += schema_str + "\n"
        except Exception as e:
            st.error(f"Table {table.table_id} not found.")
    
    return all_schemas_info

# Fetch and store schema information in session state
if "schema" not in st.session_state:
    st.session_state.schema = []

if st.session_state.schema == []:
    with st.spinner("Loading schema information..."):
        schema_for_tables = fetch_table_schemas(project_id, dataset_id)
        st.session_state.schema.append(schema_for_tables)

# Function to execute SQL queries
def execute_query(query):
    try:
        query_job = client.query(query)
        results = query_job.result().to_dataframe()
        return results
    except Exception as e:
        st.error(f"Query execution error: {e}")
        return None

# Query generation function
def qgen(prompt):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config=generation_config,
    )
    response = model.generate_content(prompt)
    return response.text

# Capture unique COUNTRY_SOURCE_IDs for selection
country_query = f"""
    SELECT DISTINCT customer_state
    FROM `{project_id}.{dataset_id}.olist_customers_datasets`;
"""

# country_data = execute_query(country_query)
# if country_data is not None:
#     countries = country_data['customer_state'].tolist()
#     selected_state = st.sidebar.selectbox("Choose a customer state", countries)

# Slider to set limit of result

#Sidebar for chart type selection
# st.sidebar.subheader("Chart Type")
# chart_types = {
#     "Bar Chart": st.sidebar.checkbox("Bar Chart"),
#     "Pie Chart": st.sidebar.checkbox("Pie Chart"),
#     "Line Chart": st.sidebar.checkbox("Line Chart"),
#     "Histogram": st.sidebar.checkbox("Histogram"),
#     "Radar Chart": st.sidebar.checkbox("Radar Chart")
# }

# # st.sidebar.radio('',['Finance','Supply chain',
# # 'Revenue growth','IT ops', 'SDLC'])

# limit = st.sidebar.slider('Limit Of Output', 0, 100, 10)

questions=['what are the potential options to reduce churn by 2%','what are the options to bring down marketing costs','key options to increase customer satisfaction','how to increase customer acquisition by 20%','how to reduce acquisition cost','how to increase retention','increase market share & profitability','what was the total sales revenue for the last quarter','can you segment our customers based on their purchase frequency','what are our most frequent purchasers buying that our least frequent purchasers aren’t',
           'are there any other distinguishing factors between the purchase frequency segments','what is the overall sentiment of our customer reviews','can you summarize the key points of feedback from our customer reviews','is there any missing data or other questions that we should be asking for customer feedback on that could improve analysis',
          'What are top 3 levers to reduce capital expenditures for our biggest projects'
          'Please provide key short-term and long-term cost reduction initiatives that and associated cost reduction potential',
          'What are the key factors for margin improvement in the next 3 quarters',
          'Highlight the key impediments impacting the enforcement of internal controls for finance',
          'Summarize the internal finance audit findings and associated potential for reducing the compliance costs',
          '']
answers="""
#####################################
What is the overall sentiment of our customer reviews? 

·  Positive Reviews: 700 (70%) 

·  Neutral Reviews: 200 (20%) 

·  Negative Reviews: 100 (10%) 

Overall Sentiment score = 0.6 which indicates positive sentiment 
########################################################################

What are the potential options to reduce churn by 2%? 

Churn Analysis Overview 

Churn Reason 

Number of Customers 

Percentage of Total Churned 

Product Quality 

500 

25% 

Poor Customer Service 

400 

20% 

High Costs 

300 

15% 

Lack of Product Availability 

250 

12.5% 

Delivery Issues 

200 

10% 

Identify Key Churn Drivers 

The top three reasons for churn account for 60% of total churn: 

Product Quality (25%) 

Poor Customer Service (20%) 

High Costs (15%) 


Suggested Strategies to Reduce Churn 

1. Improve Product Quality:: Reducing churn due to customer service issues by 40% could retain 160 customers. 

2. Enhance Customer Service : Reducing churn due to customer service issues by 40% could retain 160 customers. 

3. Address High Costs: If addressing cost-related churn reduces it by 30%, this would retain 90 customers. 


################################################################ 

What are the options to bring down marketing costs? 

 Initial Marketing Spend Across Channels: 

Digital Ads: $500,000 

In-Store Promotions: $200,000 

Email Campaigns: $150,000 

Social Media Ads: $100,000 

Ways to optimize marketing costs are 

Targeted Campaigns: +$100,000 savings by focusing on high-value customers. 

Digital Advertising Efficiency: +$75,000 savings by reallocating budget from low-conversion channels. 

In-Store and Online Integration: +$50,000 savings from unified campaign efforts. 

Social Media Optimization: +$30,000 savings by leveraging user-generated content. 

Total Projected Cost Reduction: $355,000 
 

################################################################ 

Key options to increase customer satisfaction 

 

Customer Complaints 

Number of Customers 

Product Quality 

500 

Poor Customer Service 

400 

Payment Issues 

300 

Inflexible returns policy 

250 

Delivery Issues 

200 

Based on feedback & complaints from customers, the top 5 options to increase customer satisfaction are 

Enhance Product Quality: Reducing product returns by 5% on a customer base of 50,000 could retain approximately 2,500 customers. 

Improve Customer Service: If current satisfaction scores correlate to a customer retention of 75%, improving this to 85% could increase overall satisfaction-related retention by 10%. 

Flexible Payment and Shipping Options: If the current conversion rate results in 7,500 sales, increasing this to 12,500 could add another 5,000 transactions annually, equating to $500,000 in additional sales. 

User-Friendly Returns Policy: A 15% reduction in dissatisfaction could lead to retaining an additional 1,000 customers. 

Streamlined Shipping process: Introduce multiple payment methods and flexible shipping options.
#################################################### 
Can you summarize the key points of feedback from our customer reviews? 

Key Points of Customer Feedback 

Positive Feedback 

Product Quality 

Many customers praised the quality of the products, noting that they met or exceeded expectations. High-quality essentials and seasonal items were frequently highlighted. 

Customer Service 

Positive comments about responsive and helpful customer service representatives. Customers appreciated quick resolutions to issues and friendly interactions. 

User Experience 

Customers found the online shopping experience easy to navigate, with a user-friendly interface and efficient checkout process. 

Promotions and Discounts 

Customers enjoyed the value offered through promotions, particularly buy-one-get-one deals and loyalty rewards. This incentivized them to make additional purchases. 

Fast Delivery 

Many reviews mentioned satisfaction with quick shipping times, which enhanced the overall shopping experience. 

Neutral Feedback 

Product Variety 

Some customers noted the variety of products available but expressed a desire for more options in specific categories, particularly seasonal or specialty items. 

Pricing Concerns 

Neutral comments indicated that while some products were seen as fairly priced, others were perceived as slightly higher than competitors, but customers appreciated the quality. 

Website Features 

Feedback on website features was mixed. While many found the site easy to use, some suggested improvements for better filtering options and product search capabilities. 

Negative Feedback 

Stock Availability 

Several customers expressed frustration about out-of-stock items, particularly during peak shopping seasons. This led to disappointment and potential loss of sales. 

Return Process 

Negative comments highlighted challenges with the return process, including delays and lack of clarity on return policies, which affected customer satisfaction. 

Inconsistent Product Information 

Some customers reported inconsistencies in product descriptions and images compared to the actual items received, leading to dissatisfaction. 

Delivery Issues 

A few reviews mentioned issues with shipping delays or damaged products upon arrival, impacting overall trust in the service. 

################################################################ 

Key options to increase customer satisfaction 

 

Customer Complaints 

Number of Customers 

Product Quality 

500 

Poor Customer Service 

400 

Payment Issues 

300 

Inflexible returns policy 

250 

Delivery Issues 

200 

Based on feedback & complaints from customers, the top 5 options to increase customer satisfaction are 

Enhance Product Quality: Reducing product returns by 5% on a customer base of 50,000 could retain approximately 2,500 customers. 

Improve Customer Service: If current satisfaction scores correlate to a customer retention of 75%, improving this to 85% could increase overall satisfaction-related retention by 10%. 

Flexible Payment and Shipping Options: If the current conversion rate results in 7,500 sales, increasing this to 12,500 could add another 5,000 transactions annually, equating to $500,000 in additional sales. 

User-Friendly Returns Policy: A 15% reduction in dissatisfaction could lead to retaining an additional 1,000 customers. 

Streamlined Shipping process: Introduce multiple payment methods and flexible shipping options. 

###################################
1. Top Reasons for Product Returns and Reduction Strategies

Reason for Return	Number of Returns	Percentage of Total Returns	Suggested Improvement	Expected Reduction in Returns (%)
Product Quality Issues	2,000	40%	Quality control enhancement	15%
Incorrect Item Shipped	1,250	25%	Inventory accuracy improvement	10%
Product Not as Described	1,000	20%	Improved descriptions and images	8%
Delivery Damage	750	15%	Strengthen packaging	12%
Delayed Returns Processing	500	10%	Faster return processing	5%
###################################
2. Customer Satisfaction Ratings by Product Category

Product Category	Total Reviews	Positive Reviews	Satisfaction Rating (%)	Improvement Focus
Personal Care Products	5,000	4,500	90%	Increase product range
Home Care Products	4,000	3,400	85%	Enhance fragrance options
Food & Beverages	3,500	2,800	80%	Maintain ingredient quality
Health & Wellness	2,500	2,000	80%	Improve packaging
Baby Care Products	1,200	960	80%	Expand variety in formulas
###################################
3. Optimal Product Pricing Strategies

Product Bundle Type	Current Price	Suggested Price	Average Sales Increase (%)	Profit Margin Increase (%)
Personal Care Bundle	$25	$20	15%	10%
Home Essentials Kit	$30	$27	12%	8%
Family Food Pack	$40	$38	10%	7%
Health Supplements Duo	$50	$47	8%	6%
Baby Care Essentials	$60	$55	5%	4%
###################################
4. Primary Factors Affecting Product Quality Perception

Quality Factor	Customer Complaints	Percentage of Total Feedback	Improvement Action	Expected Quality Score Increase (%)
Ingredient Quality	800	35%	Increase ingredient transparency	10%
Product Durability	600	25%	Enhance durability testing	8%
Packaging Quality	500	20%	Use eco-friendly, durable materials	7%
Product Scent Consistency	300	13%	Standardize scent formulas	5%
Product Size Consistency	200	7%	Standardize packaging sizes	3%
###################################
5. Impact of Product Variety on Customer Loyalty

Customer Segment	Preferred Product Category	Number of Purchases	Repeat Purchase Increase (%)	Feedback on Variety
Frequent Buyers	Personal Care	20,000	25%	Positive
Moderate Buyers	Home Care	15,000	20%	Neutral
Light Buyers	Food & Beverages	12,000	10%	Positive
Seasonal Shoppers	Holiday Specials	8,000	18%	Very Positive
Infrequent Shoppers	Basic Essentials	5,000	5%	Neutral
###################################
6. Most Effective Customer Feedback Channels

Feedback Channel	Responses Collected	Percentage of Total Feedback	Engagement Rate (%)	Insight Frequency (%)
Online Reviews	3,500	40%	60%	70%
Post-Purchase Surveys	2,500	30%	45%	50%
Social Media Polls	1,000	20%	50%	60%
Customer Service Calls	750	5%	30%	40%
Focus Groups	250	5%	70%	80%
###################################
7. Main Challenges in Achieving Higher Product Ratings

Challenge	Customer Complaints	Percentage of Total Complaints	Suggested Solution	Expected Improvement (%)
Delivery Damage	1,200	25%	Use improved packaging	15%
Product Transparency	1,000	20%	Clarify product information	10%
Slow Complaint Response	750	15%	Implement faster support response	8%
Stock Availability	600	12%	Better stock management	10%
Pricing Concerns	450	8%	Maintain competitive pricing	5%
###################################
8. Seasonal Demand Strategies for Product Sales

Strategy	Product Category	Average Sales Increase (%)	Cost of Implementation ($)	Customer Engagement Increase (%)
Holiday-Themed Bundles	Personal Care	30%	10,000	20%
Limited Edition Products	Home Care	25%	8,000	18%
Seasonal Ads	Food & Beverages	20%	5,000	15%
Targeted Discounts	Health & Wellness	15%	7,000	12%
Loyalty Rewards	Baby Care	10%	3,000	10%
###################################
9. Customer Segments Based on Purchase Frequency and Product Preferences

Segment	Purchase Frequency	Product Preferences	Engagement with Promotions	Average Order Value ($)
Frequent Buyers	5+ per year	High-quality essentials	High	50
Moderate Buyers	3-4 per year	Promotional bundles	Moderate	40
Light Buyers	1-2 per year	Essentials on sale	Low	30
Seasonal Shoppers	1-2 per season	Seasonal items	Very High	60
Infrequent Shoppers	<1 per year	Basics only	Minimal	25
###################################
10. Impact of Product Innovation on Customer Retention

Customer Group	Engaged with New Products	Retention Rate Increase (%)	Average Purchase Value ($)	Satisfaction Increase (%)
New Customers	5,000	20%	35	15%
Repeat Customers	10,000	15%	45	10%
High-Value Customers	2,500	25%	60	20%
Moderate-Value Customers	7,500	10%	40	8%
Low-Value Customers	12,500	8%	30	5%
###################################
"""
# Handle user input and query generation
if user_input:
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    mock_question=True
    # for i in questions:
    if True:
        # if i.strip().lower()==user_input.strip().lower() :
        if True:
            # mock_question=True
            prompt=f"""a user is asking questions. user questions={user_input}
            
            answer the user on the basis of following following question answer. write full answer of question {user_input} as it is with data(table).dont make any changes in answer.
            {answers}.
            #########################
            dont add any additional comment just answer the questions if answer having table u can use table with answers.
            use bold for heading and bullet points as well for better representaions of answers.
            """
            
            with st.spinner("Please Wait..."):
                result = qgen(prompt)
                st.session_state.messages.append({"role": "assistant", "content":result, "summary": ''})

        
    if mock_question==False:
        my_prompt = f"""act as a sql query writer for BigQuery database. We have the following schema:
        project_id = "data-driven-cx"
        dataset_id = "EDW_ECOM"
        {st.session_state.schema[0]}
        Write a SQL query for user input
        user input-{user_input}.
        Write only the executable query without any comments or additional text.
        """
        
        with st.spinner("Generating query..."):
            final_query = qgen(my_prompt)
            cleaned_query = final_query.replace("```sql", "").replace("```", "").strip()
        
        try:
            with st.spinner("Executing query..."):
                data = execute_query(cleaned_query)
            st.session_state.messages.append({"role": "assistant", "content": final_query, "results": data})
        except Exception as e:
            st.error(f"Query execution error: {e}")
            if "editable_sql" not in st.session_state:
                st.session_state.editable_sql = final_query

        # Display the SQL query editor and execution button if there's a query to edit
        if "editable_sql" in st.session_state:
            st.write("## Edit and Re-Execute the Query")
            edited_sql = st.text_area("Edit Query", st.session_state.editable_sql)
            
            if st.button('Submit'):
                with st.spinner("Executing query..."):
                    data = execute_query(edited_sql)
                if data is not None:
                    st.session_state.messages.append({"role": "assistant", "content": edited_sql, "results": data})
                    st.session_state.editable_sql = edited_sql

# Display all the chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='card'>{message['content']}</div>", unsafe_allow_html=True)
        if "results" in message:
            # if not message["results"].empty: 
            st.dataframe(message["results"])
        # if "summary" in message:
        #     st.write(message["summary"])



# # Visualization section
# if "messages" in st.session_state:
#     # Find the last message that contains results
#     last_data = None
#     for message in reversed(st.session_state.messages):
#         if "results" in message:
#             last_data = message["results"]
#             break
    
#     if last_data is not None and not last_data.empty:
#         st.write("## Data Visualization")

#         numeric_columns = last_data.select_dtypes(include=['float64', 'int64']).columns
#         non_numeric_columns = last_data.select_dtypes(exclude=['float64', 'int64']).columns

#         for chart_type, selected in chart_types.items():
#             if selected:
#                 st.write("## Data Visualization")
#                 st.write(f"### {chart_type}")
#                 if chart_type == "Bar Chart" and len(numeric_columns) >= 1 and len(non_numeric_columns) >= 1:
#                     fig = px.bar(last_data, x=non_numeric_columns[0], y=numeric_columns[0], color=non_numeric_columns[0])
#                     st.plotly_chart(fig)
#                 elif chart_type == "Pie Chart" and len(numeric_columns) >= 1 and len(non_numeric_columns) >= 1:
#                     fig = px.pie(last_data, values=numeric_columns[0], names=non_numeric_columns[0])
#                     st.plotly_chart(fig)
#                 elif chart_type == "Line Chart" and len(numeric_columns) >= 1 and len(non_numeric_columns) >= 1:
#                     fig = px.line(last_data, x=non_numeric_columns[0], y=numeric_columns[0])
#                     st.plotly_chart(fig)
#                 elif chart_type == "Histogram" and len(numeric_columns) >= 1:
#                     fig = px.histogram(last_data, x=numeric_columns[0])
#                     st.plotly_chart(fig)
#                 elif chart_type == "Radar Chart" and len(numeric_columns) > 1:
#                     fig = go.Figure()
#                     fig.add_trace(go.Scatterpolar(
#                         r=last_data[numeric_columns].mean().values,
#                         theta=numeric_columns,
#                         fill='toself'
#                     ))
#                     fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
#                     st.plotly_chart(fig)
#                 else:
#                     st.warning(f"Not enough appropriate columns to plot a {chart_type}.")
#     else:
#         st.write("")
