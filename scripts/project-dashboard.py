#!/usr/bin/env python3
"""
Project and Quality Manager Dashboard
Provides comprehensive project status and metrics for PM/QM oversight
"""

import os
import json
import subprocess
import requests
from datetime import datetime
from pathlib import Path
import glob

class ProjectDashboard:
    def __init__(self):
        self.project_root = Path.cwd()
        self.backend_url = "http://localhost:8000"
        self.frontend_urls = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"]
        
    def check_server_health(self):
        """Check health of backend and frontend servers"""
        print("🏥 Server Health Check")
        print("=" * 50)
        
        # Check backend
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend: HEALTHY")
                backend_data = response.json()
                print(f"   Status: {backend_data.get('status', 'unknown')}")
            else:
                print("⚠️  Backend: UNHEALTHY")
        except requests.exceptions.RequestException:
            print("❌ Backend: NOT RUNNING")
        
        # Check frontend
        frontend_running = False
        for url in self.frontend_urls:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"✅ Frontend: RUNNING on {url}")
                    frontend_running = True
                    break
            except requests.exceptions.RequestException:
                continue
        
        if not frontend_running:
            print("❌ Frontend: NOT RUNNING")
    
    def get_git_status(self):
        """Get current git status and recent activity"""
        print("\n📈 Git Status")
        print("=" * 50)
        
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("❌ Not a git repository")
                return
            
            # Get current branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True)
            current_branch = result.stdout.strip()
            print(f"🌿 Current branch: {current_branch}")
            
            # Get recent commits
            result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print("📝 Recent commits:")
                for line in result.stdout.strip().split('\n'):
                    print(f"   {line}")
            else:
                print("📝 No recent commits")
            
            # Check for uncommitted changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print("⚠️  Uncommitted changes:")
                for line in result.stdout.strip().split('\n')[:5]:
                    print(f"   {line}")
                lines = result.stdout.strip().split('\n')
                if len(lines) > 5:
                    print(f"   ... and {len(lines) - 5} more")
            else:
                print("✅ Working directory clean")
                
        except Exception as e:
            print(f"❌ Error checking git status: {e}")
    
    def analyze_task_files(self):
        """Analyze task files and calculate completion metrics"""
        print("\n📋 Task Analysis")
        print("=" * 50)
        
        task_files = list(self.project_root.glob("**/tasks-*.md")) + list(self.project_root.glob("**/prd-*.md"))
        
        if not task_files:
            print("⚠️  No task files found")
            return
        
        total_tasks = 0
        completed_tasks = 0
        task_details = []
        
        for task_file in task_files:
            try:
                with open(task_file, 'r') as f:
                    content = f.read()
                
                pending = content.count('[ ]')
                completed = content.count('[x]')
                
                total_tasks += pending + completed
                completed_tasks += completed
                
                task_details.append({
                    'file': task_file.name,
                    'pending': pending,
                    'completed': completed,
                    'total': pending + completed
                })
                
            except Exception as e:
                print(f"❌ Error reading {task_file}: {e}")
        
        if total_tasks > 0:
            completion_rate = (completed_tasks / total_tasks) * 100
            print(f"📊 Overall completion: {completion_rate:.1f}% ({completed_tasks}/{total_tasks})")
            
            print("\n📁 Task files breakdown:")
            for detail in task_details:
                if detail['total'] > 0:
                    file_rate = (detail['completed'] / detail['total']) * 100
                    print(f"   {detail['file']}: {file_rate:.1f}% ({detail['completed']}/{detail['total']})")
        else:
            print("📊 No tasks found in files")
    
    def check_code_quality(self):
        """Check code quality metrics"""
        print("\n🔍 Code Quality Check")
        print("=" * 50)
        
        # Check for Python files
        python_files = list(self.project_root.glob("**/*.py"))
        if python_files:
            print(f"🐍 Python files: {len(python_files)}")
        
        # Check for TypeScript files
        ts_files = list(self.project_root.glob("**/*.ts")) + list(self.project_root.glob("**/*.tsx"))
        if ts_files:
            print(f"📘 TypeScript files: {len(ts_files)}")
        
        # Check for test files
        test_files = list(self.project_root.glob("**/test_*.py")) + list(self.project_root.glob("**/*.test.ts"))
        if test_files:
            print(f"🧪 Test files: {len(test_files)}")
        
        # Check for documentation files
        doc_files = list(self.project_root.glob("**/*.md")) + list(self.project_root.glob("**/*.txt"))
        if doc_files:
            print(f"📚 Documentation files: {len(doc_files)}")
        
        # Check for configuration files
        config_files = list(self.project_root.glob("**/*.json")) + list(self.project_root.glob("**/*.yaml")) + list(self.project_root.glob("**/*.yml"))
        if config_files:
            print(f"⚙️  Configuration files: {len(config_files)}")
    
    def check_system_resources(self):
        """Check system resource usage"""
        print("\n💻 System Resources")
        print("=" * 50)
        
        try:
            # Check disk usage
            result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    if len(parts) >= 5:
                        usage = parts[4]
                        print(f"💾 Disk usage: {usage}")
            
            # Check Python cache
            cache_dirs = list(self.project_root.glob("**/__pycache__"))
            if cache_dirs:
                print(f"🗂️  Python cache directories: {len(cache_dirs)}")
            else:
                print("🗂️  Python cache: Clean")
                
        except Exception as e:
            print(f"❌ Error checking system resources: {e}")
    
    def get_project_metrics(self):
        """Get key project metrics"""
        print("\n📊 Project Metrics")
        print("=" * 50)
        
        # Count files by type
        file_types = {
            'Python': len(list(self.project_root.glob("**/*.py"))),
            'TypeScript': len(list(self.project_root.glob("**/*.ts")) + list(self.project_root.glob("**/*.tsx"))),
            'Markdown': len(list(self.project_root.glob("**/*.md"))),
            'JSON': len(list(self.project_root.glob("**/*.json"))),
            'YAML': len(list(self.project_root.glob("**/*.yaml")) + list(self.project_root.glob("**/*.yml"))),
        }
        
        for file_type, count in file_types.items():
            if count > 0:
                print(f"📄 {file_type} files: {count}")
        
        # Count directories
        directories = [d for d in self.project_root.iterdir() if d.is_dir()]
        print(f"📁 Directories: {len(directories)}")
    
    def generate_recommendations(self):
        """Generate PM/QM recommendations"""
        print("\n💡 PM/QM Recommendations")
        print("=" * 50)
        
        recommendations = []
        
        # Check if servers are running
        try:
            requests.get(f"{self.backend_url}/health", timeout=2)
            backend_running = True
        except:
            backend_running = False
        
        if not backend_running:
            recommendations.append("🔧 Start development servers")
        
        # Check for uncommitted changes
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                recommendations.append("📝 Commit pending changes")
        except:
            pass
        
        # Check task completion
        task_files = list(self.project_root.glob("**/tasks-*.md"))
        if task_files:
            recommendations.append("📋 Review and update task status")
        
        # Check for Python cache
        cache_dirs = list(self.project_root.glob("**/__pycache__"))
        if len(cache_dirs) > 10:
            recommendations.append("🧹 Clean Python cache directories")
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"{i}. {rec}")
        else:
            print("✅ No immediate actions required")
    
    def run_full_dashboard(self):
        """Run the complete dashboard"""
        print("🚀 Project and Quality Manager Dashboard")
        print("=" * 60)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📂 Project: {self.project_root.name}")
        print("=" * 60)
        
        self.check_server_health()
        self.get_git_status()
        self.analyze_task_files()
        self.check_code_quality()
        self.check_system_resources()
        self.get_project_metrics()
        self.generate_recommendations()
        
        print("\n" + "=" * 60)
        print("🎯 Dashboard complete! Use this information to guide project management decisions.")
        print("=" * 60)

def main():
    dashboard = ProjectDashboard()
    dashboard.run_full_dashboard()

if __name__ == "__main__":
    main() 