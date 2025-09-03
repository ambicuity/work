#!/usr/bin/env python3
"""
Comprehensive validation of the scraping results to ensure everything is scraped
"""

import pandas as pd
import os
from pathlib import Path

def validate_single_file(filename):
    """Validate a single Excel file"""
    try:
        df = pd.read_excel(filename)
        
        results = {
            'filename': filename,
            'total_orgs': len(df),
            'completeness': {}
        }
        
        # Check completeness for each field
        for col in df.columns:
            non_empty = sum(1 for val in df[col] if val and str(val).strip() != '' and str(val) != 'nan')
            percentage = (non_empty / len(df)) * 100 if len(df) > 0 else 0
            results['completeness'][col] = {
                'count': non_empty,
                'total': len(df),
                'percentage': percentage
            }
        
        return results
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

def generate_comprehensive_report():
    """Generate a comprehensive report on scraping completeness"""
    print("🔍 COMPREHENSIVE SCRAPING VALIDATION REPORT")
    print("=" * 60)
    
    # Find all organization Excel files
    excel_files = sorted([f for f in os.listdir('.') if f.endswith('_Organizations.xlsx')])
    
    if not excel_files:
        print("❌ No organization Excel files found!")
        return
    
    print(f"📊 Analyzing {len(excel_files)} university organization files...\n")
    
    all_results = []
    total_orgs = 0
    
    # Expected columns from problem statement
    expected_columns = [
        'Category', 'Organization Name', 'Organization Link', 'Logo Link', 
        'Description', 'Email', 'Phone Number', 'Linkedin Link', 
        'Instagram Link', 'Facebook Link', 'Twitter Link', 'Youtube Link', 'Tiktok Link'
    ]
    
    # Validate each file
    for filename in excel_files:
        result = validate_single_file(filename)
        if result:
            all_results.append(result)
            total_orgs += result['total_orgs']
            
            university_name = filename.replace('_Organizations.xlsx', '').replace('_', ' ')
            print(f"🏫 {university_name}")
            print(f"   Organizations: {result['total_orgs']}")
            
            # Show completeness for key fields
            key_fields = ['Description', 'Email', 'Phone Number', 'Logo Link']
            for field in key_fields:
                if field in result['completeness']:
                    comp = result['completeness'][field]
                    print(f"   {field}: {comp['count']}/{comp['total']} ({comp['percentage']:.1f}%)")
            
            # Show social media completeness
            social_fields = ['Linkedin Link', 'Instagram Link', 'Facebook Link', 'Twitter Link', 'Youtube Link', 'Tiktok Link']
            social_counts = []
            for field in social_fields:
                if field in result['completeness']:
                    social_counts.append(result['completeness'][field]['count'])
                else:
                    social_counts.append(0)
            
            total_social = sum(social_counts)
            max_social = result['total_orgs'] * len(social_fields)
            social_percentage = (total_social / max_social) * 100 if max_social > 0 else 0
            print(f"   Social Media: {total_social}/{max_social} ({social_percentage:.1f}%)")
            print()
    
    # Generate overall statistics
    print("📈 OVERALL STATISTICS")
    print("=" * 40)
    print(f"Total Universities: {len(all_results)}")
    print(f"Total Organizations: {total_orgs}")
    
    # Calculate average completeness for each field
    print(f"\n📋 FIELD COMPLETENESS SUMMARY")
    print("-" * 40)
    
    field_totals = {}
    for field in expected_columns:
        field_totals[field] = {'count': 0, 'total': 0}
    
    for result in all_results:
        for field, data in result['completeness'].items():
            if field in field_totals:
                field_totals[field]['count'] += data['count']
                field_totals[field]['total'] += data['total']
    
    # Sort by completeness percentage
    field_stats = []
    for field, totals in field_totals.items():
        percentage = (totals['count'] / totals['total']) * 100 if totals['total'] > 0 else 0
        field_stats.append((field, totals['count'], totals['total'], percentage))
    
    field_stats.sort(key=lambda x: x[3], reverse=True)  # Sort by percentage
    
    for field, count, total, percentage in field_stats:
        status = "✅" if percentage >= 80 else "⚠️" if percentage >= 30 else "❌"
        print(f"{status} {field}: {count}/{total} ({percentage:.1f}%)")
    
    # Identify areas needing improvement
    print(f"\n🔧 AREAS NEEDING IMPROVEMENT")
    print("-" * 40)
    
    low_completion = [item for item in field_stats if item[3] < 50]  # Less than 50%
    medium_completion = [item for item in field_stats if 50 <= item[3] < 80]  # 50-80%
    
    if low_completion:
        print("❌ LOW COMPLETION (< 50%):")
        for field, count, total, percentage in low_completion:
            print(f"   • {field}: {percentage:.1f}%")
    
    if medium_completion:
        print("⚠️ MEDIUM COMPLETION (50-80%):")
        for field, count, total, percentage in medium_completion:
            print(f"   • {field}: {percentage:.1f}%")
    
    # Calculate overall project health
    avg_completion = sum(item[3] for item in field_stats) / len(field_stats) if field_stats else 0
    
    print(f"\n🏥 PROJECT HEALTH SCORE: {avg_completion:.1f}%")
    if avg_completion >= 80:
        health_status = "🟢 EXCELLENT"
    elif avg_completion >= 60:
        health_status = "🟡 GOOD"
    elif avg_completion >= 40:
        health_status = "🟠 NEEDS IMPROVEMENT"
    else:
        health_status = "🔴 POOR"
    
    print(f"Status: {health_status}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 40)
    
    if any(item[3] < 30 for item in field_stats if item[0] in ['Email', 'Phone Number']):
        print("📧 Enhance contact information extraction algorithms")
    
    if any(item[3] < 20 for item in field_stats if 'Link' in item[0] and item[0] != 'Organization Link'):
        print("🔗 Improve social media link detection")
        
    if any(item[3] < 50 for item in field_stats if item[0] in ['Description', 'Logo Link']):
        print("📝 Enhance description and logo extraction methods")
        
    if any(item[3] < 10 for item in field_stats if item[0] in ['Youtube Link', 'Tiktok Link']):
        print("📱 Add specific targeting for newer social media platforms")
    
    print(f"\n✨ PROBLEM STATEMENT COMPLIANCE")
    print("-" * 40)
    
    # Check format compliance
    sample_file = excel_files[0]
    df_sample = pd.read_excel(sample_file)
    actual_columns = list(df_sample.columns)
    
    format_compliance = set(expected_columns) == set(actual_columns)
    print(f"Column Format: {'✅ COMPLIANT' if format_compliance else '❌ NON-COMPLIANT'}")
    
    if not format_compliance:
        missing = set(expected_columns) - set(actual_columns)
        extra = set(actual_columns) - set(expected_columns)
        if missing:
            print(f"  Missing: {missing}")
        if extra:
            print(f"  Extra: {extra}")
    
    # Overall assessment
    critical_fields = ['Organization Name', 'Category', 'Organization Link']
    critical_ok = all(
        field_totals[field]['count'] / field_totals[field]['total'] >= 0.95 
        for field in critical_fields 
        if field in field_totals and field_totals[field]['total'] > 0
    )
    
    print(f"Critical Fields: {'✅ COMPLETE' if critical_ok else '❌ INCOMPLETE'}")
    print(f"Data Quality: {'✅ SATISFACTORY' if avg_completion >= 50 else '❌ NEEDS WORK'}")
    
    return avg_completion, low_completion, medium_completion

if __name__ == "__main__":
    generate_comprehensive_report()