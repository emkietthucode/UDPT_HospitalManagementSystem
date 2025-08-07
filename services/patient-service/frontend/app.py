# frontend/app.py
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change in production

# Configuration
PATIENT_SERVICE_URL = os.getenv('PATIENT_SERVICE_URL', 'http://127.0.0.1:8001')

class PatientService:
    """Client for communicating with Patient Service"""
    
    def __init__(self, base_url):
        self.base_url = base_url
    
    def get_patients(self, skip=0, limit=100, name=None, phone=None, email=None):
        """Get list of patients with optional filters"""
        params = {'skip': skip, 'limit': limit}
        if name: 
            params['name'] = name
        if phone:
            params['phone'] = phone
        if email:
            params['email'] = email
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/patients", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching patients: {e}")
            return []
    
    def get_patient(self, patient_id):
        """Get a specific patient by ID"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/patients/{patient_id}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching patient {patient_id}: {e}")
            return None
    
    def create_patient(self, patient_data):
        """Create a new patient"""
        try:
            print('Raw patient data 1:', self.base_url)
            response = requests.post(
                f"{self.base_url}/api/v1/patients", 
                json=patient_data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error creating patient: {e}")
            return None
    
    def update_patient(self, patient_id, patient_data):
        """Update an existing patient"""
        try:
            response = requests.put(
                f"{self.base_url}/api/v1/patients/{patient_id}",
                json=patient_data
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error updating patient {patient_id}: {e}")
            return None
    
    def delete_patient(self, patient_id):
        """Delete a patient"""
        try:
            response = requests.delete(f"{self.base_url}/api/v1/patients/{patient_id}")
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Error deleting patient {patient_id}: {e}")
            return False
    
    def get_patients_count(self, name=None, phone=None, email=None):
        """Get total count of patients"""
        params = {}
        if name:
            params['name'] = name
        if phone:
            params['phone'] = phone
        if email:
            params['email'] = email
        
        try:
            response = requests.get(f"{self.base_url}/api/v1/patients/search/count", params=params)
            response.raise_for_status()
            return response.json().get('total', 0)
        except requests.RequestException as e:
            print(f"Error getting patient count: {e}")
            return 0

# Initialize service client
patient_service = PatientService(PATIENT_SERVICE_URL)

@app.route('/')
def index():
    """Main page - List all patients with search"""
    # Get search parameters
    name = request.args.get('name', '').strip()
    phone = request.args.get('phone', '').strip()
    email = request.args.get('email', '').strip()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Calculate pagination
    skip = (page - 1) * per_page
    
    # Get patients and total count
    patients = patient_service.get_patients(
        skip=skip, 
        limit=per_page, 
        name=name or None, 
        phone=phone or None, 
        email=email or None
    )
    
    total = patient_service.get_patients_count(
        name=name or None, 
        phone=phone or None, 
        email=email or None
    )
    
    # Calculate pagination info
    total_pages = (total + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('patients/index.html', 
                         patients=patients,
                         total=total,
                         page=page,
                         per_page=per_page,
                         total_pages=total_pages,
                         has_prev=has_prev,
                         has_next=has_next,
                         search_name=name,
                         search_phone=phone,
                         search_email=email)

@app.route('/patients/new', methods=['GET', 'POST'])
def new_patient():
    """Create new patient form"""
    if request.method == 'POST':
        
        patient_data = {
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'date_of_birth': request.form.get('date_of_birth'),
            'gender': request.form.get('gender')
        }
        print('Raw patient data:', patient_data)
        # Remove empty fields
        patient_data = {k: v for k, v in patient_data.items() if v}
        
        result = patient_service.create_patient(patient_data)
        if result:
            flash('Bệnh nhân đã được tạo thành công!', 'success')
            return redirect(url_for('index'))
        else:
            print('Có lỗi xảy ra khi tạo bệnh nhân!')
            # flash('Có lỗi xảy ra khi tạo bệnh nhân!', 'error')
    
    return render_template('patients/new.html')

@app.route('/patients/<patient_id>')
def view_patient(patient_id):
    """View patient details"""
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash('Không tìm thấy bệnh nhân!', 'error')
        return redirect(url_for('index'))
    
    return render_template('patients/view.html', patient=patient)

@app.route('/patients/<patient_id>/edit', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """Edit patient form"""
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash('Không tìm thấy bệnh nhân!', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        patient_data = {
            'full_name': request.form.get('full_name'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'date_of_birth': request.form.get('date_of_birth'),
            'gender': request.form.get('gender')
        }
        
        # Remove empty fields
        patient_data = {k: v for k, v in patient_data.items() if v}
        
        result = patient_service.update_patient(patient_id, patient_data)
        if result:
            flash('Thông tin bệnh nhân đã được cập nhật!', 'success')
            return redirect(url_for('view_patient', patient_id=patient_id))
        else:
            flash('Có lỗi xảy ra khi cập nhật thông tin!', 'error')
    
    return render_template('patients/edit.html', patient=patient)

@app.route('/patients/<patient_id>/delete', methods=['POST'])
def delete_patient(patient_id):
    """Delete patient"""
    if patient_service.delete_patient(patient_id):
        flash('Bệnh nhân đã được xóa!', 'success')
    else:
        flash('Có lỗi xảy ra khi xóa bệnh nhân!', 'error')
    
    return redirect(url_for('index'))

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

# Utility filters for templates
@app.template_filter('datetime')
def datetime_filter(value):
    """Format datetime for display"""
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M')
        except:
            return value
    return value

if __name__ == '__main__':
    app.run(debug=True, port=5000)