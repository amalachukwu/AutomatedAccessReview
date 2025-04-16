import pandas as pd
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize Flask application
app = Flask(__name__)

# Load sample data (in a real implementation, this would connect to a database)
def load_sample_data():
    # Sample user access rights data
    data = {
        'access_id': range(1, 11),
        'user_id': ['U001', 'U002', 'U003', 'U001', 'U002', 'U004', 'U003', 'U005', 'U004', 'U005'],
        'user_name': ['John Doe', 'Jane Smith', 'Mike Johnson', 'John Doe', 'Jane Smith', 
                       'Sarah Williams', 'Mike Johnson', 'Tom Brown', 'Sarah Williams', 'Tom Brown'],
        'department': ['IT', 'HR', 'Finance', 'IT', 'HR', 'Marketing', 'Finance', 'Sales', 'Marketing', 'Sales'],
        'system_name': ['CRM', 'HRIS', 'ERP', 'Email Gateway', 'Recruitment Portal', 
                         'Analytics Platform', 'Accounting System', 'CRM', 'Website Admin', 'Sales Database'],
        'access_level': ['Admin', 'User', 'Read-Only', 'Admin', 'Admin', 
                          'User', 'Admin', 'User', 'Admin', 'User'],
        'date_granted': ['2024-01-15', '2024-02-20', '2024-01-10', '2023-11-05', '2024-03-01',
                          '2024-02-15', '2023-10-10', '2024-03-10', '2023-12-20', '2024-01-25'],
        'last_reviewed': ['2024-03-15', '2024-03-15', '2024-03-15', '2024-02-05', '2024-03-15',
                           None, '2024-02-10', None, '2024-03-01', None],
        'risk_level': ['High', 'Medium', 'Medium', 'High', 'Medium', 
                        'Low', 'High', 'Low', 'Medium', 'Low'],
        'reviewer_id': ['M001', 'M002', 'M003', 'M001', 'M002', 'M004', 'M003', 'M005', 'M004', 'M005'],
        'reviewer_name': ['Alex Manager', 'Rachel Director', 'David Leader', 'Alex Manager', 'Rachel Director',
                           'Lisa Supervisor', 'David Leader', 'Mark Head', 'Lisa Supervisor', 'Mark Head'],
        'review_status': ['Pending', 'Pending', 'Pending', 'Pending', 'Pending', 
                           'Pending', 'Pending', 'Pending', 'Pending', 'Pending']
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data)
    
    # Convert date strings to datetime objects
    df['date_granted'] = pd.to_datetime(df['date_granted'])
    df['last_reviewed'] = pd.to_datetime(df['last_reviewed'])
    
    return df

# Calculate next review date based on risk level
def calculate_review_schedule(df):
    today = datetime.datetime.now()
    
    # Define review frequency based on risk level (in days)
    risk_frequencies = {
        'High': 30,    # Monthly
        'Medium': 90,  # Quarterly
        'Low': 180     # Semi-annually
    }
    
    # Calculate next review date
    next_review_dates = []
    for _, row in df.iterrows():
        # Use last review date if available, otherwise use grant date
        if pd.notna(row['last_reviewed']):
            last_date = row['last_reviewed']
        else:
            last_date = row['date_granted']
        
        # Calculate next review based on risk level
        days_to_add = risk_frequencies[row['risk_level']]
        next_date = last_date + datetime.timedelta(days=days_to_add)
        
        # If next date is in the past, set to today
        if next_date < today:
            next_date = today
            
        next_review_dates.append(next_date)
    
    # Add next review date to DataFrame
    df['next_review_date'] = next_review_dates
    return df

# Identify access reviews that need to be initiated
def identify_due_reviews(df):
    today = datetime.datetime.now()
    upcoming_window = today + datetime.timedelta(days=7)  # 7-day window
    
    # Filter for reviews due now or in the upcoming window
    due_reviews = df[(df['next_review_date'] <= upcoming_window) & 
                      (df['review_status'] == 'Pending')]
    
    return due_reviews

# Send notification emails to reviewers (simulated)
def send_notifications(due_reviews):
    # Group by reviewer to send consolidated emails
    reviewers = due_reviews.groupby(['reviewer_id', 'reviewer_name'])
    
    for (reviewer_id, reviewer_name), reviews in reviewers:
        # In a real implementation, this would send an actual email
        print(f"------ EMAIL TO: {reviewer_name} ({reviewer_id}) ------")
        print(f"Subject: Access Review Certification Required")
        print(f"Dear {reviewer_name},")
        print(f"You have {len(reviews)} access certifications pending review.")
        print("Please review the following access rights:")
        
        for _, review in reviews.iterrows():
            print(f"- User: {review['user_name']} ({review['user_id']})")
            print(f"  System: {review['system_name']} (Access Level: {review['access_level']})")
            print(f"  Risk Level: {review['risk_level']}")
        
        print(f"Please complete your review by: {reviews['next_review_date'].min().strftime('%Y-%m-%d')}")
        print(f"Review URL: http://localhost:5000/review/{reviewer_id}")
        print("--------------------------------------------------\n")

# Initialize global data
access_data = load_sample_data()
access_data = calculate_review_schedule(access_data)

# Flask routes
@app.route('/')
def index():
    global access_data
    # Count statistics for dashboard
    total_access = len(access_data)
    high_risk = len(access_data[access_data['risk_level'] == 'High'])
    pending_reviews = len(access_data[access_data['review_status'] == 'Pending'])
    overdue = len(identify_due_reviews(access_data))
    
    return render_template('index.html', 
                           total_access=total_access,
                           high_risk=high_risk,
                           pending_reviews=pending_reviews,
                           overdue=overdue)

@app.route('/review/<reviewer_id>')
def review_page(reviewer_id):
    global access_data
    # Filter access data for this reviewer
    reviewer_items = access_data[access_data['reviewer_id'] == reviewer_id]
    reviewer_name = reviewer_items['reviewer_name'].iloc[0] if not reviewer_items.empty else "Unknown"
    
    return render_template('review.html',
                           reviewer_id=reviewer_id,
                           reviewer_name=reviewer_name,
                           items=reviewer_items.to_dict('records'))

@app.route('/certify', methods=['POST'])
def certify_access():
    global access_data
    
    access_id = int(request.form.get('access_id'))
    decision = request.form.get('decision')
    comments = request.form.get('comments', '')
    reviewer_id = request.form.get('reviewer_id')
    
    # Update the review status in the dataframe
    idx = access_data.index[access_data['access_id'] == access_id].tolist()[0]
    access_data.at[idx, 'review_status'] = decision
    access_data.at[idx, 'last_reviewed'] = datetime.datetime.now()
    access_data.at[idx, 'review_comments'] = comments
    
    # Recalculate next review date
    access_data = calculate_review_schedule(access_data)
    
    # Log the certification action
    print(f"Access ID {access_id} certified as '{decision}' by {reviewer_id}")
    print(f"Comments: {comments}")
    
    # Redirect back to the review page
    return redirect(url_for('review_page', reviewer_id=reviewer_id))

@app.route('/reports')
def reports():
    global access_data
    
    # Generate summary data for reports
    status_summary = access_data['review_status'].value_counts().to_dict()
    risk_summary = access_data['risk_level'].value_counts().to_dict()
    system_summary = access_data['system_name'].value_counts().to_dict()
    
    return render_template('reports.html',
                           status_summary=status_summary,
                           risk_summary=risk_summary,
                           system_summary=system_summary)

# Scheduled job to run access reviews
def scheduled_review_job():
    global access_data
    print("Running scheduled access review check...")
    due_reviews = identify_due_reviews(access_data)
    
    if not due_reviews.empty:
        print(f"Found {len(due_reviews)} reviews due for certification")
        send_notifications(due_reviews)
    else:
        print("No reviews due at this time")

# Start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_review_job, 'interval', hours=24)  # Run daily
    scheduler.start()
    print("Scheduler started")

# Main entry point
if __name__ == '__main__':
    # Start the background scheduler
    start_scheduler()
    
    # Run initial review job
    scheduled_review_job()
    
    # Start the Flask application
    app.run(debug=True)