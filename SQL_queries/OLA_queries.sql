create database OLA_Ride_Analysis;

use OLA_Ride_Analysis;

select * from ola_data;

select count(*) as total_rows from ola_data;


select * from ola_data where booking_status = "Success" and is_ride_completed=1;

select vehicle_type,round(avg(ride_distance),2) as average from ola_data group by vehicle_type;

select count(*) as canceled_rides_by_customer from ola_data where canceled_rides_by_customer != "Not Applicable";

select customer_id,count(*) as rides from ola_data group by customer_id order by rides desc limit 5;

select count(*) as canceled_rides_by_driver from ola_data where canceled_rides_by_driver ="Personal & Car related issue";

select max(driver_ratings) as max_rating, min(driver_ratings) as min_rating from ola_data where vehicle_type="Prime Sedan";

select * from ola_data where payment_method="UPI";

select vehicle_type,round(avg(customer_rating),2) as average_customer_rating from ola_data group by vehicle_type order by average_customer_rating desc;

select sum(booking_value) as Revenue from ola_data where is_ride_completed=1;

select booking_id,customer_id,booking_status,incomplete_rides,incomplete_rides_reason from ola_data where booking_status="Success" and Incomplete_rides="Yes";


