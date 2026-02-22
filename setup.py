"""
ApplyAI - Setup Script
Helps users configure the application
"""
import os
import shutil
import sys

def setup_config():
    """Copy template config files if they don't exist"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    templates = [
        'user_config.template.yaml',
        'user_profile.template.yaml',
        'resumes_config.template.yaml',
        'schedule_config.template.yaml'
    ]
    
    print("🔧 ApplyAI Setup")
    print("=" * 50)
    
    for template in templates:
        template_path = os.path.join(data_dir, template)
        config_name = template.replace('.template', '')
        config_path = os.path.join(data_dir, config_name)
        
        if os.path.exists(template_path) and not os.path.exists(config_path):
            shutil.copy(template_path, config_path)
            print(f"✅ Created {config_name}")
        elif os.path.exists(config_path):
            print(f"ℹ️  {config_name} already exists")
    
    print("\n📋 Next Steps:")
    print("1. Edit data/user_config.yaml with your credentials")
    print("2. Edit data/user_profile.yaml with your profile info")
    print("3. Run: python ui/main.py")
    print("\n🚀 Ready to start applying!")

if __name__ == "__main__":
    setup_config()
