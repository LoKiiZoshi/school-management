import openai
from django.conf import settings
import json
from datetime import datetime

# Configure OpenAI API key
openai.api_key = getattr(settings, 'OPENAI_API_KEY', '')

def generate_text(prompt, max_tokens=500, temperature=0.7):
    """
    Generate text using OpenAI API
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specializing in educational fee management and financial documentation."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating content: {str(e)}"

def generate_fee_report(report_data):
    """
    Generate an AI-powered fee report analysis
    """
    prompt = f"""
    Generate a comprehensive fee report analysis for {report_data['current_month']} with the following data:
    
    Monthly Revenue: ${report_data['monthly_revenue']}
    Payment Statistics:
    - Total Payments: {report_data['payment_stats']['total_payments']}
    - Paid Payments: {report_data['payment_stats']['paid_payments']}
    - Pending Payments: {report_data['payment_stats']['pending_payments']}
    - Overdue Payments: {report_data['payment_stats']['overdue_payments']}
    
    Please provide:
    1. Key performance indicators analysis
    2. Collection efficiency assessment
    3. Recommendations for improvement
    4. Trends and patterns identified
    5. Action items for the next month
    
    Format as a professional report.
    """
    
    return generate_text(prompt, max_tokens=800)

def generate_payment_reminder(payment_data):
    """
    Generate personalized payment reminders
    """
    if isinstance(payment_data, dict):
        prompt = f"""
        Generate a polite but firm payment reminder for:
        Student: {payment_data.get('student_name', 'Student')}
        Fee Type: {payment_data.get('fee_type', 'Fee')}
        Amount Due: ${payment_data.get('amount_due', 0)}
        Due Date: {payment_data.get('due_date', 'Not specified')}
        Days Overdue: {payment_data.get('days_overdue', 0)}
        
        Make it professional, understanding, and include next steps.
        """
    else:
        prompt = f"Generate a payment reminder: {payment_data}"
    
    return generate_text(prompt, max_tokens=300)

def generate_policy_document(policy_type, institution_name, requirements):
    """
    Generate policy documents
    """
    prompt = f"""
    Generate a {policy_type} for {institution_name}.
    
    Requirements:
    {requirements}
    
    Include:
    1. Clear terms and conditions
    2. Procedures and processes
    3. Important dates and deadlines
    4. Contact information placeholders
    5. Legal disclaimers
    
    Format as a professional policy document.
    """
    
    return generate_text(prompt, max_tokens=1000)

def generate_financial_insights(financial_data):
    """
    Generate financial insights and recommendations
    """
    prompt = f"""
    Analyze this financial data and provide actionable insights:
    
    {json.dumps(financial_data, indent=2, default=str)}
    
    Focus on:
    1. Revenue trends and patterns
    2. Collection efficiency
    3. Risk factors
    4. Opportunities for improvement
    5. Specific recommendations
    
    Provide practical, actionable advice.
    """
    
    return generate_text(prompt, max_tokens=700)

def generate_student_communication(communication_type, student_data):
    """
    Generate various student communications
    """
    prompt = f"""
    Generate a {communication_type} for student communication:
    
    Student Information:
    {json.dumps(student_data, indent=2, default=str)}
    
    Make it:
    1. Professional and friendly
    2. Clear and concise
    3. Actionable
    4. Appropriate for the context
    """
    
    return generate_text(prompt, max_tokens=400)