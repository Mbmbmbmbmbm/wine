import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
st.set_option('deprecation.showPyplotGlobalUse', False)

# Import necessary libraries
# Function to load the dataset
@st.cache_data  # Cache the function to enhance performance
def load_data():
    # Define the file path
    file_path = 'https://raw.githubusercontent.com/Mbmbmbmbmbm/titanic/main/wine_market.csv'
    
    # Load the CSV file into a pandas dataframe
    df = pd.read_csv(file_path)
    
    # Cleaning data
    df = df[df['Marital_Status'] != 'Absurd']
    df = df[df['Marital_Status'] != 'YOLO']
    df['Marital_Status'] = df['Marital_Status'].replace('Alone', 'Single')
    df['Income'].fillna(df['Income'].median(), inplace=True)
    df=df.drop(2233) #the 666666 income outlier

    #Drop the 3 people that are about 120 years old
    df=df.drop(192)
    df=df.drop(239)
    df=df.drop(339)
    
    # Create age groups and add as a new column
    df['Age'] = 2023 - df['Year_Birth']
    bin_edges = [27, 40, 50, 60, 90]
    bin_labels = ['27-40', '40-50', '50-60', '60+']
    df['AgeGroup'] = pd.cut(df['Age'], bins=bin_edges, labels=bin_labels, right=False)

    return df

# Load the data using the defined function
df = load_data()

st.title('Customer Personality Analysis Dashboard')
st.sidebar.header("Filters 📊")

# Introduction

# HR Attrition Dashboard

st.markdown(""" Welcome to the Wine market Dashboard🍷. Due to the everchanging financial environment of today it is necessary for businesses to have a significant understanding of their target audience to better market their products and allocate time and money into development of under supplied user-segments. The following Wine Market dashboard includes a filter option where it is possible to create a specific segment from 6 different parameters and thereafter see the visualized data for the specific group.""")

with st.expander("**How to use the dashboard**"):
                 st.markdown("""Sidebar Usage: The sidebar on the left allows you to filter customers by their characteristics. You can select specific attributes to focus on and adjust filters to explore the data.

Dashboard Output: The dashboard provides descriptive statistics of customer spending habits, helping you gain insights into their behaviors and preferences.

""")
                             

# Sidebar filter: Age Group
selected_age_group = st.sidebar.multiselect("Select Age Groups 🕰️", df['AgeGroup'].unique().tolist(), default=df['AgeGroup'].unique().tolist())
if not selected_age_group:
    st.warning("Please select an age group from the sidebar ⚠️")
    st.stop()
filtered_df = df[df['AgeGroup'].isin(selected_age_group)]

# Sidebar filter: Education
Education = df['Education'].unique().tolist()
selected_Education = st.sidebar.multiselect("Select Education 🏢", Education, default=Education)
if not selected_Education:
    st.warning("Please select an Education from the sidebar ⚠️")
    st.stop()
filtered_df = filtered_df[filtered_df['Education'].isin(selected_Education)]

# Sidebar filter: Marital Status
Marital_Status = df['Marital_Status'].unique().tolist()
selected_Marital_Status = st.sidebar.multiselect("Select Marital Status💍", Marital_Status, default=Marital_Status)
if not selected_Marital_Status:
    st.warning("Please select a Marital Status from the sidebar ⚠️")
    st.stop()
filtered_df = filtered_df[filtered_df['Marital_Status'].isin(selected_Marital_Status)]

#Sidebar filter: complaint
# Create a mapping from string to original values 
complain_mapping = {'Yes': 1, 'No': 0}
# Get the unique values and create a list of strings for the sidebar
Complain = ['Yes' if x == 1 else 'No' for x in df['Complain'].unique().tolist()]

selected_Complainer = st.sidebar.multiselect("Has customer complained?😠", Complain, default=Complain)
if not selected_Complainer:
    st.warning("Please select a complaint status from the sidebar ⚠️")
    st.stop()
# Map the selected values back to the original values for filtering
selected_Complainer_mapped = [complain_mapping[val] for val in selected_Complainer]

filtered_df = filtered_df[filtered_df['Complain'].isin(selected_Complainer_mapped)]

# Sidebar filter:  Income Range
min_income = int(df['Income'].min())
max_income = int(df['Income'].max())
income_range = st.sidebar.slider("Select Income Range 💰", min_income, max_income, (min_income, max_income))
filtered_df = filtered_df[(filtered_df['Income'] >= income_range[0]) & (filtered_df['Income'] <= income_range[1])]

# Sidebar filter:  Recency
min_recent = df['Recency'].min()
max_recent = df['Recency'].max()
min_recent = int(min_recent)
max_recent = int(max_recent)
recent_range = st.sidebar.slider("Select days since Last Purchase", min_recent, max_recent, (min_recent, max_recent))
filtered_df = filtered_df[(filtered_df['Recency'] >= recent_range[0]) & (filtered_df['Recency'] <= recent_range[1])]


# Displaying the Attrition Analysis header
st.header("Customer Analysis 📊")

# Dropdown to select the type of visualization
visualization_option = st.selectbox(
    'Select Visualization 🎨', 
    [ 'Campaign Acceptence', 'Spending by Product Type', 'Channel Overview' ]
)

if visualization_option == 'Campaign Acceptence':
    @st.cache_data  # Cache the function to enhance performance
    def load_camp_data():
        df_camp = ['ID', 'AcceptedCmp1', 'AcceptedCmp2', 'AcceptedCmp3', 'AcceptedCmp4', 'AcceptedCmp5', 'Response']

        df_camp = df[df_camp]

        df_camp = df_camp.melt(id_vars=['ID'], var_name='Campaign', value_name='Reaction')

        return df_camp

    df_camp = load_camp_data()

    # Extract the IDs from 'filtered_df'
    filtered_ids = filtered_df['ID']

    # Filter 'df_camp' based on the IDs in 'filtered_df'
    df_camp = df_camp[df_camp['ID'].isin(filtered_ids)]

    df_camp = df_camp.groupby('Campaign').agg(Count=pd.NamedAgg(column='Reaction', aggfunc='count'),Acceptance_rate=pd.NamedAgg(column='Reaction', aggfunc=lambda x: (sum(x) / len(x)) * 100),).reset_index()

    df_camp['Campaign'] = df_camp['Campaign'].replace({'AcceptedCmp1': '1st','AcceptedCmp2': '2nd','AcceptedCmp3': '3rd','AcceptedCmp4': '4th','AcceptedCmp5': '5th','Response': '6th'})

    plt.figure()
    sns.barplot(x='Campaign', y='Acceptance_rate', data=df_camp)
    plt.ylabel('Acceptance Rate (%)')
    plt.xlabel('Campaign')
    plt.title('Acceptance Rates of Each Marketing Campaign')
    st.pyplot()
    st.markdown("The above graph visualizes the total amount spent on different goods in the last 2 years. The goods are spread out across the product groups: fish, fruits, gold, meat, sweets and wine")



elif visualization_option == 'Spending by Product Type':
    @st.cache_data  # Cache the function to enhance performance
    def load_amount_data():
        df_amount = ['ID', 'MntWines','MntFruits','MntMeatProducts','MntFishProducts','MntSweetProducts','MntGoldProds']

        df_amount=df[df_amount]

        df_amount = df_amount.melt(id_vars=['ID'], var_name='Product_Type', value_name='Amount')

        return df_amount

    df_amount = load_amount_data()

    # Extract the IDs from 'filtered_df'
    filtered_ids= filtered_df['ID']

    # Filter 'df_camp' based on the IDs in 'filtered_df'
    df_amount = df_amount[df_amount['ID'].isin(filtered_ids)]
    
    df_amount['Product_Type'] = df_amount['Product_Type'].replace({'MntWines': 'Wine','MntFruits': 'Fruits','MntMeatProducts': 'Meat','MntFishProducts': 'Fish','MntSweetProducts': 'Sweets','MntGoldProds': 'Gold'})

    df_sum = df_amount.groupby('Product_Type')['Amount'].sum().reset_index()

    plt.figure()
    sns.barplot(x='Product_Type', y='Amount', data=df_sum)
    plt.ylabel('Total Amount')
    plt.xlabel('Product Type')
    plt.title('Total Amount Bought of Each Product Type')
    st.pyplot()
    st.markdown("The above graph visualizes the acceptance rate for if the customer has accepted an offer in a specific campaign.  The value in the x-axis illustrates the number of the specific campaign sent to them and the y-axis illustrates the acceptance rate of the specific campaign")
    
    selected_columns_1 = ['MntWines','MntFruits','MntMeatProducts','MntFishProducts','MntSweetProducts','MntGoldProds']
    df_des2 = filtered_df[selected_columns_1].describe().T
    df_des2
    
elif visualization_option == 'Channel Overview':
    # Melt the dataframe to have channels as a single column
    df_melted = df.melt(id_vars='MntWines', value_vars=['NumWebPurchases', 'NumCatalogPurchases', 'NumStorePurchases'],
                    var_name='Channel', value_name='Number_of_Purchases')

    # Create a categorical scatter plot

    data = {
    'Channel': ['Web'] * filtered_df['NumWebPurchases'].sum() +
               ['Catalog'] * filtered_df['NumCatalogPurchases'].sum() +
               ['Store'] * filtered_df['NumStorePurchases'].sum(),
    'Purchases': range(filtered_df['NumWebPurchases'].sum() +
                       filtered_df['NumCatalogPurchases'].sum() +
                       filtered_df['NumStorePurchases'].sum())
    }

    df_purchases = pd.DataFrame(data)

    #Create a subplot with 2 rows and 1 column


    #Create a count plot on the second row
    sns.countplot(x='Channel', data=df_purchases)
    plt.title('Countplot of Number of Purchases by Channel')

    plt.tight_layout()
    st.pyplot()
    st.markdown("The above graph visualizes the place of the specific purchases. The value in the x-axis illustrates the place of the purchases and the y-axis illustrates the amount bought at the location. ")

    selected_columns = ['NumWebPurchases','NumCatalogPurchases','NumStorePurchases']
    df_des1 = filtered_df[selected_columns].describe().T
    df_des1

