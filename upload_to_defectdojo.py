#!/usr/bin/env python3
import os
import sys
import requests
import json
from datetime import datetime
from urllib.parse import urlparse

class DefectDojoUploader:
    def __init__(self, base_url, api_token):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Token {api_token}',
            'Content-Type': 'application/json'
        }
    
    def test_connection(self):
        """Test DefectDojo API connection"""
        try:
            response = requests.get(f'{self.base_url}/api/v2/users/', headers=self.headers)
            if response.status_code == 200:
                print("✅ DefectDojo API connection successful")
                return True
            else:
                print(f"❌ API connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {str(e)}")
            return False
    
    def create_product(self, product_name, description="Automated Security Assessment"):
        """Create a new product in DefectDojo"""
        # First check if product exists
        response = requests.get(
            f'{self.base_url}/api/v2/products/',
            headers=self.headers,
            params={'name': product_name}
        )
        
        if response.status_code == 200:
            products = response.json()['results']
            if products:
                product_id = products[0]['id']
                print(f"✅ Using existing product: {product_name} (ID: {product_id})")
                return product_id
        
        # Create new product
        data = {
            'name': product_name,
            'description': description,
            'prod_type': 1,  # Research and Development
            'business_criticality': 'medium'
        }
        
        response = requests.post(f'{self.base_url}/api/v2/products/', headers=self.headers, json=data)
        
        if response.status_code == 201:
            product_id = response.json()['id']
            print(f"✅ Product created: {product_name} (ID: {product_id})")
            return product_id
        else:
            print(f"❌ Failed to create product: {response.text}")
            return None
    
    def list_engagements(self, product_id):
        """List all engagements for a product"""
        response = requests.get(
            f'{self.base_url}/api/v2/engagements/',
            headers=self.headers,
            params={'product': product_id}
        )
        
        if response.status_code == 200:
            return response.json().get('results', [])
        return []
    
    def delete_engagement(self, engagement_id):
        """Delete an engagement by ID"""
        response = requests.delete(
            f'{self.base_url}/api/v2/engagements/{engagement_id}/',
            headers=self.headers
        )
        return response.status_code == 204
    
    def delete_previous_engagements(self, product_id):
        """Delete all previous engagements for a product to prevent duplicates"""
        engagements = self.list_engagements(product_id)
        
        if not engagements:
            print("✅ No previous engagements to delete")
            return True
        
        print(f"🗑️ Found {len(engagements)} previous engagement(s) to delete...")
        
        for engagement in engagements:
            eid = engagement['id']
            ename = engagement['name']
            print(f"   Deleting engagement: {ename} (ID: {eid})")
            
            if self.delete_engagement(eid):
                print(f"   ✅ Successfully deleted engagement ID {eid}")
            else:
                print(f"   ❌ Failed to delete engagement ID {eid}")
                return False
        
        print("✅ All previous engagements deleted successfully")
        return True
    
    def create_engagement(self, product_id, engagement_name, target_url):
        """Create a new engagement"""
        data = {
            'name': engagement_name,
            'product': product_id,
            'target_start': datetime.now().strftime('%Y-%m-%d'),
            'target_end': datetime.now().strftime('%Y-%m-%d'),
            'engagement_type': 'CI/CD',
            'status': 'In Progress',
            'description': f'Automated OWASP ZAP security scan for {target_url}'
        }
        
        response = requests.post(f'{self.base_url}/api/v2/engagements/', headers=self.headers, json=data)
        
        if response.status_code == 201:
            engagement_id = response.json()['id']
            print(f"✅ Engagement created: {engagement_name} (ID: {engagement_id})")
            return engagement_id
        else:
            print(f"❌ Failed to create engagement: {response.text}")
            return None
    
    def import_scan(self, engagement_id, scan_file, scan_type="ZAP Scan"):
        """Import OWASP ZAP scan results to DefectDojo"""
        
        print(f"📤 Uploading {scan_file} as {scan_type}...")
        
        data = {
            'scan_type': scan_type,
            'engagement': engagement_id,
            'verified': True,
            'active': True,
            'scan_date': datetime.now().strftime('%Y-%m-%d'),
            'minimum_severity': 'Info',
            'close_old_findings': True,
            'push_to_jira': False,
            'skip_duplicates': True,
            'do_not_reactivate': False
        }
        
        files = {'file': open(scan_file, 'rb')}
        headers = {'Authorization': f'Token {self.api_token}'}
        
        try:
            response = requests.post(
                f'{self.base_url}/api/v2/import-scan/',
                headers=headers,
                files=files,
                data=data
            )
            
            files['file'].close()
            
            if response.status_code == 201:
                import_data = response.json()
                test_id = import_data.get('test', 'unknown')
                findings_count = len(import_data.get('findings_added', []))
                print(f"✅ Scan imported successfully!")
                print(f"   Test ID: {test_id}")
                print(f"   Findings imported: {findings_count}")
                return True
            else:
                print(f"❌ Failed to import scan: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {str(e)}")
            return False

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 upload_to_defectdojo.py <report_directory> <target_url>")
        sys.exit(1)
    
    report_dir = sys.argv[1]
    target_url = sys.argv[2]
    
    defectdojo_url = os.getenv('DEFECT_DOJO_URL', 'http://localhost:8080')
    api_token = os.getenv('DEFECT_DOJO_API_TOKEN')
    
    if not api_token:
        print("❌ DEFECT_DOJO_API_TOKEN environment variable not set")
        sys.exit(1)
    
    if not os.path.exists(report_dir):
        print(f"❌ Report directory {report_dir} does not exist")
        sys.exit(1)
    
    uploader = DefectDojoUploader(defectdojo_url, api_token)
    
    if not uploader.test_connection():
        sys.exit(1)
    
    domain = urlparse(target_url).netloc.replace('.', '_')
    product_name = f"Security_Assessment_{domain}"
    
    try:
        # Get or create product
        product_id = uploader.create_product(product_name)
        if not product_id:
            sys.exit(1)
        
        # Delete previous engagements to prevent duplicates
        if not uploader.delete_previous_engagements(product_id):
            print("❌ Failed to delete previous engagements")
            sys.exit(1)
        
        # Create new engagement
        engagement_name = f"OWASP_ZAP_Comprehensive_Scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        engagement_id = uploader.create_engagement(product_id, engagement_name, target_url)
        if not engagement_id:
            sys.exit(1)
        
        # Upload ONLY full scan XML (avoids baseline duplication)
        full_scan_xml = os.path.join(report_dir, 'full_scan_report.xml')
        
        if os.path.exists(full_scan_xml):
            if uploader.import_scan(engagement_id, full_scan_xml, "ZAP Scan"):
                print(f"\n🎉 Successfully uploaded clean comprehensive ZAP scan to DefectDojo!")
                print(f"📊 No duplicate findings - accurate vulnerability metrics")
                print(f"🔗 View results: {defectdojo_url}/engagement/{engagement_id}")
                print(f"🔗 Dashboard: {defectdojo_url}/dashboard")
            else:
                print(f"\n❌ Failed to upload full scan report")
        else:
            print("❌ Full scan XML report not found")
            print("💡 Make sure your ZAP full scan generates XML with -x parameter")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
 
