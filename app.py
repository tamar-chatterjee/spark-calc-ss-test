from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  

@app.route('/calculate', methods=['POST'])
def calculate():
    
    storage_size_tb = float(request.form['storage_size'])  
    data_egress_tb = float(request.form['data_egress'])  
    usage_duration = int(request.form['usage_duration'])  

 
    storage_size_gb = storage_size_tb * 1024
    data_egress_gb = data_egress_tb * 1024


    spark_base_cost_per_gb = 0.015 * usage_duration 
    spark_base_cost = spark_base_cost_per_gb * storage_size_gb  

    if storage_size_tb > 0.1:
        max_discount = 0.5  
        discount_ramp_start = 0.1  
        discount_ramp_end = 2.0  

        
        discount_percentage = min(
            max_discount,
            (storage_size_tb - discount_ramp_start) / (discount_ramp_end - discount_ramp_start) * max_discount
        )

        spark_discounted_cost = spark_base_cost * (1 - discount_percentage)
    else:
        spark_discounted_cost = spark_base_cost

   

    spark_egress_cost = 0 
    spark_total_cost = spark_discounted_cost + spark_egress_cost

    aws_storage_cost = 0.023 * storage_size_gb * usage_duration
    aws_egress_cost = 0.09 * data_egress_gb * usage_duration

    gcp_storage_cost = 0.02 * storage_size_gb * usage_duration
    gcp_egress_cost = 0.12 * data_egress_gb * usage_duration

    azure_storage_cost = 0.0184 * storage_size_gb * usage_duration
    azure_egress_cost = 0.087 * data_egress_gb * usage_duration

   
    if storage_size_tb <= 25:
        mediashuttle_storage_cost = 0.0284 * storage_size_gb * usage_duration 
        mediashuttle_egress_cost = 0  
    else:
        mediashuttle_storage_cost = 0.021 * storage_size_gb * usage_duration 
        mediashuttle_egress_cost = 0.09 * data_egress_gb * usage_duration 


    mediashuttle_total_cost = mediashuttle_storage_cost + mediashuttle_egress_cost


   
    googledrive_cost = None 
    if storage_size_tb <= 0.2:
        googledrive_cost = 2.99 * usage_duration
    elif 0.2 < storage_size_tb <= 2:
        googledrive_cost = 9.99 * usage_duration
    elif 2 < storage_size_tb <= 5:
        googledrive_cost = 24.99 * usage_duration
    elif 5 < storage_size_tb <= 10:
        googledrive_cost = 49.99 * usage_duration
    elif 10 < storage_size_tb <= 20:
        googledrive_cost = 99.99 * usage_duration
    elif 20 < storage_size_tb <= 30:
        googledrive_cost = 149.99 * usage_duration

    
    dropbox_cost = 0 
    if storage_size_tb <= 2:
        dropbox_cost = 11.99 * usage_duration
    elif 2 < storage_size_tb <= 3:
        dropbox_cost = 19.99 * usage_duration
    elif 3 < storage_size_tb <= 15:
        dropbox_cost = 54.00 * usage_duration
    else:
        
        additional_tb = storage_size_tb - 15
        additional_cost = (additional_tb // 5) * 30
        dropbox_cost = (90 + additional_cost) * usage_duration


   
    spark_total_cost = spark_discounted_cost + spark_egress_cost
    aws_total_cost = aws_storage_cost + aws_egress_cost
    gcp_total_cost = gcp_storage_cost + gcp_egress_cost
    azure_total_cost = azure_storage_cost + azure_egress_cost

    return jsonify({
        'spark_cost': spark_total_cost,
        'aws_cost': aws_total_cost,
        'gcp_cost': gcp_total_cost,
        'azure_cost': azure_total_cost,
        'mediashuttle_cost': mediashuttle_total_cost,
        'googledrive_cost': googledrive_cost,
        'dropbox_cost': dropbox_cost
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
