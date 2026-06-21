import streamlit as st
from database import run_query
import plotly.express as px
from streamlit_option_menu import option_menu


st.set_page_config(
    page_title="OLA Analytics",
    page_icon="🚖",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.title("📊 OLA Ride Analytics Dashboard")
st.caption("Ola Ride insights powered by SQL Server")
st.sidebar.title("🚖OLA Ride Analytics")



if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

with st.sidebar:
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.page = "Dashboard"

    if st.button("🗄️ SQL Analysis", use_container_width=True):
        st.session_state.page = "SQL Analysis"

    if st.button("📈 Power BI Report", use_container_width=True):
        st.session_state.page = "Power BI Report"

page = st.session_state.page

if page == "Dashboard":
    col1,col2,col3,col4,col5=st.columns(5)

    with col1:
        total_bookings = run_query("select count(*) as total_bookings FROM ola_data")

        st.metric("Total Bookings",f"{total_bookings.iloc[0]['total_bookings']:,}")
    
    with col2:
        revenue = run_query("select sum(booking_value) as revenue from ola_data where is_ride_completed=1")

        st.metric("Revenue",f"₹{revenue.iloc[0]['revenue']:,.0f}")
    
    with col3:
        success_rate=run_query("select round(100.0 * sum(case when Booking_Status='Success' and is_ride_completed=1 then 1 else 0 end)/count(*),2) SuccessRate FROM ola_data")

        st.metric("Success Rate",f"{success_rate.iloc[0]['SuccessRate']}%")
    with col4:
        cancel_rate=run_query("select round(100.0 * sum(case when booking_status !='Success' then 1 else 0 end) / count(*), 2) as cancellation_rate from ola_data")
        
        st.metric("Cancellation Rate",f"{cancel_rate.iloc[0]['cancellation_rate']}%")
    with col5:
        Incomplete_ride=run_query("select round(100.0 * sum(case when booking_status ='Success' and is_ride_completed=0 then 1 else 0 end) / count(*), 2) as Incomplete_ride_rate from ola_data")
        
        st.metric("Incomplete Ride Rate",f"{Incomplete_ride.iloc[0]['Incomplete_ride_rate']}%")
    

    col1,col2,col3=st.columns(3)

    with col1:
        revenue = run_query("select vehicle_type, sum(booking_value) as Revenue from ola_data where Booking_Status='Success' and is_ride_completed=1 group by vehicle_type order by Revenue desc")

        fig = px.bar(revenue,x="vehicle_type",y="Revenue",title="Revenue by Vehicle Type",text_auto='.2s')
        

        fig.update_layout(
            title={
                'text': 'Revenue by Vehicle Type',
                'font': {'size': 20}
                },

            plot_bgcolor='White',
            paper_bgcolor='White',

            xaxis_title='Vehicle Type',
            yaxis_title='Revenue (₹)',

            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            ),
            height=300
            )
        st.plotly_chart(fig,use_container_width=True)

    with col2:
        trends=run_query("select hour, count(*) as Total_bookings from ola_data group by hour order by hour")

        fig=px.line(trends,x="hour",y="Total_bookings",markers=True)

        fig.update_layout(
            title={
                "text": "Booking Trend Over Time",
                "font": {"size": 20}
            },
            plot_bgcolor='White',
            paper_bgcolor='White',

            xaxis_title='Hours',
            yaxis_title='Bookings',
            margin=dict(
                l=20,
                r=20,
                t=50,
                b=20
            ),
            height=300
        )

        fig.update_xaxes(tickmode="linear",tick0=0,dtick=3)

        st.plotly_chart(fig,use_container_width=True)
    
    
    with col3:
        donut=run_query("select booking_status, count(*) as total_bookings from ola_data group by booking_status order by booking_status desc")

        fig=px.pie(donut,names="booking_status",values="total_bookings",hole=0.55)

        fig.update_layout(
            title={
                "text": "Booking Status Distribution",
                "font": {"size": 20}
            },
            plot_bgcolor='White',
            paper_bgcolor='White',

            legend_title="Status",
            margin=dict(
                l=40,
                r=20,
                t=50,
                b=10
            ),
            height=300
        )

        st.plotly_chart(fig,use_container_width=True)


elif page == "SQL Analysis":

    date_df=run_query("select max(date) as Max_date, min(date) as Min_date from ola_data")
    vehicle_df=run_query("select distinct(vehicle_type) from ola_data order by vehicle_type")
    booking_df=run_query("select distinct(booking_status) from ola_data order by booking_status")

    with st.sidebar:

        st.header("Filters")

        date_range = st.date_input(
            "Date Range",
            value=(date_df["Min_date"][0],date_df["Max_date"][0])
        )

        vehicle = st.multiselect(
            "Vehicle Type",
            vehicle_df["vehicle_type"].tolist()
        )

        booking_status = st.multiselect(
            "Booking Status",
            booking_df["booking_status"].tolist()
        )

        booking_id = st.text_input(
            "Search Booking ID"
        )

        customer_id = st.text_input(
            "Search Customer ID"
        )

    conditions = []

    if vehicle:
        vehicle_values = "','".join(vehicle)
        conditions.append(
            f"vehicle_type IN ('{vehicle_values}')"
        )

    if booking_status:
        status_values = "','".join(booking_status)
        conditions.append(
            f"booking_status IN ('{status_values}')"
        )

    if len(date_range) == 2:
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[1].strftime("%Y-%m-%d")

        conditions.append(f"DATE(Date) BETWEEN '{start_date}' AND '{end_date}'")

    if booking_id:
        conditions.append(
            f"booking_id = '{booking_id}'"
        )
    
    if customer_id:
        conditions.append(
            f"customer_id = '{customer_id}'"
        )

    where_clause = ""

    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    filter_clause = ""

    if conditions:
        filter_clause = " AND " + " AND ".join(conditions)

    

    tab1,tab2,tab3,tab4,tab5,tab6,tab7,tab8,tab9,tab10 = st.tabs(["All Successful Bookings","Average Ride Distance Per Vehicle type","Cancelled By Customers","Top 5 Customers","Cancelled By Drivers","Max and Min Driver's Ratings","Payment Types","Average Customer Ratings","Revenue(Successful Bookings)","Incomplete Rides"])

    with tab1:
        all_success=run_query(f"select * from ola_data where booking_status = 'Success' and is_ride_completed=1 {filter_clause};")
        st.dataframe(all_success)

        csv = all_success.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="all_success.csv",
            mime="text/csv"
        )
    
    with tab2:
        avg_ride=run_query(f"select vehicle_type,round(avg(ride_distance),2) as average from ola_data {where_clause} group by vehicle_type;")
        st.dataframe(avg_ride)

        csv = avg_ride.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="avg_ride.csv",
            mime="text/csv"
        )
    
    with tab3:
        customer_cancel=run_query(f"select count(*) as canceled_rides_by_customer from ola_data where canceled_rides_by_customer != 'Not Applicable' {filter_clause};")
        st.dataframe(customer_cancel)

        csv = customer_cancel.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="customer_cancel.csv",
            mime="text/csv"
        )
    
    with tab4:
        top5=run_query(f"select customer_id,count(*) as rides from ola_data {where_clause} group by customer_id order by rides desc limit 5;")
        st.dataframe(top5)

        csv = top5.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="top5.csv",
            mime="text/csv"
        )
    
    with tab5:
        driver_cancel=run_query(f"select count(*) as canceled_rides_by_driver from ola_data where canceled_rides_by_driver ='Personal & Car related issue' {filter_clause};")
        st.dataframe(driver_cancel)

        csv = driver_cancel.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="driver_cancel.csv",
            mime="text/csv"
        )
    
    with tab6:
        max_min=run_query(f"select max(driver_ratings) as max_rating, min(driver_ratings) as min_rating from ola_data where vehicle_type='Prime Sedan' {filter_clause};")
        st.dataframe(max_min)

        csv = max_min.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="max_min.csv",
            mime="text/csv"
        )

    with tab7:
        payment=run_query(f"select * from ola_data where payment_method='UPI' {filter_clause};")
        st.dataframe(payment)

        csv = payment.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="payment.csv",
            mime="text/csv"
        )
    
    with tab8:
        rating=run_query(f"select vehicle_type,round(avg(customer_rating),2) as average_customer_rating from ola_data {where_clause} group by vehicle_type order by average_customer_rating desc;")
        st.dataframe(rating)

        csv = rating.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="rating.csv",
            mime="text/csv"
        )
    
    with tab9:
        revenues=run_query(f"select sum(booking_value) as Revenue from ola_data where is_ride_completed=1 {filter_clause};")
        st.dataframe(revenues)

        csv = revenues.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="revenues.csv",
            mime="text/csv"
        )
    
    with tab10:
        incomplete=run_query(f"select booking_id,customer_id,booking_status,incomplete_rides,incomplete_rides_reason from ola_data where booking_status='Success' and Incomplete_rides='Yes' {filter_clause};")
        st.dataframe(incomplete)

        csv = incomplete.to_csv(index=False)

        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="incomplete.csv",
            mime="text/csv"
        )
    
    


elif page == "Power BI Report":
    tab1,tab2,tab3,tab4,tab5=st.tabs(["Overall","Vehicle_type","Revenue","Cancellation","Ratings"])

    with tab1:
        st.image(r"C:\Users\ukesh\OneDrive\Desktop\Project\Ola_Ride_Insights\Screenshots\Overall_page.png", use_container_width=True)

    with tab2:
        st.image(r"C:\Users\ukesh\OneDrive\Desktop\Project\Ola_Ride_Insights\Screenshots\Vehicle_type_page.png", use_container_width=True)

    with tab3:
        st.image(r"C:\Users\ukesh\OneDrive\Desktop\Project\Ola_Ride_Insights\Screenshots\Revenue_page.png", use_container_width=True)

    with tab4:
        st.image(r"C:\Users\ukesh\OneDrive\Desktop\Project\Ola_Ride_Insights\Screenshots\cancellation_page.png", use_container_width=True)

    with tab5:
        st.image(r"C:\Users\ukesh\OneDrive\Desktop\Project\Ola_Ride_Insights\Screenshots\Ratings_page.png", use_container_width=True)