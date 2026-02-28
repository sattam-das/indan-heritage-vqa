"""
AUTOMATED QA GENERATION SCRIPT (NO SPLITS)
============================================
Generates question-answer pairs for Indian Heritage VQA dataset
No train/val/test splitting - just creates the full dataset
"""

import json
import csv
from pathlib import Path
from datetime import datetime
import random

# Configuration
DATA_DIR = Path("data")
CLEANED_DIR = DATA_DIR / "raw_metadata"
METADATA_FILE = CLEANED_DIR / "metadata_consolidated.json"
OUTPUT_DIR = DATA_DIR / "annotations"

# Monument Knowledge Base
MONUMENT_INFO = {
    "Taj Mahal": {
        "location": "Agra",
        "state": "Uttar Pradesh",
        "built_by": "Shah Jahan",
        "built_for": "Mumtaz Mahal",
        "year_built": "1632-1653",
        "century": "17th century",
        "architectural_style": "Mughal",
        "material": "White marble",
        "religion": "Islamic",
        "purpose": "Mausoleum",
        "unesco_year": "1983",
        "description": "Ivory-white marble mausoleum"
    },
    "Qutub Minar": {
        "location": "Delhi",
        "state": "Delhi",
        "built_by": "Qutb-ud-din Aibak",
        "year_built": "1192",
        "century": "12th century",
        "architectural_style": "Indo-Islamic",
        "material": "Red sandstone",
        "religion": "Islamic",
        "purpose": "Victory tower",
        "height": "73 meters",
        "unesco_year": "1993"
    },
    "Red Fort Delhi": {
        "location": "Delhi",
        "state": "Delhi",
        "built_by": "Shah Jahan",
        "year_built": "1639-1648",
        "century": "17th century",
        "architectural_style": "Mughal",
        "material": "Red sandstone",
        "religion": "Islamic",
        "purpose": "Palace fort",
        "unesco_year": "2007"
    },
    "Hampi Monuments": {
        "location": "Hampi",
        "state": "Karnataka",
        "built_by": "Vijayanagara Empire",
        "year_built": "14th-16th century",
        "century": "14th-16th century",
        "architectural_style": "Dravidian",
        "material": "Granite",
        "religion": "Hindu",
        "purpose": "Temple complex",
        "unesco_year": "1986"
    },
    "Ajanta Caves": {
        "location": "Aurangabad",
        "state": "Maharashtra",
        "built_by": "Buddhist monks",
        "year_built": "2nd century BCE - 6th century CE",
        "century": "Ancient",
        "architectural_style": "Rock-cut",
        "material": "Basalt rock",
        "religion": "Buddhist",
        "purpose": "Monastery",
        "unesco_year": "1983"
    },
    "Ellora Caves": {
        "location": "Aurangabad",
        "state": "Maharashtra",
        "built_by": "Various dynasties",
        "year_built": "6th-10th century CE",
        "century": "6th-10th century",
        "architectural_style": "Rock-cut",
        "material": "Basalt rock",
        "religion": "Hindu, Buddhist, Jain",
        "purpose": "Temple complex",
        "unesco_year": "1983"
    },
    "Konark Sun Temple": {
        "location": "Konark",
        "state": "Odisha",
        "built_by": "King Narasimhadeva I",
        "year_built": "1250",
        "century": "13th century",
        "architectural_style": "Kalinga",
        "material": "Khondalite rocks",
        "religion": "Hindu",
        "purpose": "Sun temple",
        "deity": "Surya",
        "unesco_year": "1984"
    },
    "Khajuraho Temples": {
        "location": "Khajuraho",
        "state": "Madhya Pradesh",
        "built_by": "Chandela dynasty",
        "year_built": "950-1050 CE",
        "century": "10th-11th century",
        "architectural_style": "Nagara",
        "material": "Sandstone",
        "religion": "Hindu, Jain",
        "purpose": "Temple complex",
        "unesco_year": "1986"
    },
    "Mahabalipuram Monuments": {
        "location": "Mahabalipuram",
        "state": "Tamil Nadu",
        "built_by": "Pallava dynasty",
        "year_built": "7th-8th century",
        "century": "7th-8th century",
        "architectural_style": "Dravidian",
        "material": "Granite",
        "religion": "Hindu",
        "purpose": "Temple complex",
        "unesco_year": "1984"
    },
    "Fatehpur Sikri": {
        "location": "Fatehpur Sikri",
        "state": "Uttar Pradesh",
        "built_by": "Akbar",
        "year_built": "1571-1585",
        "century": "16th century",
        "architectural_style": "Mughal",
        "material": "Red sandstone",
        "religion": "Islamic",
        "purpose": "Capital city",
        "unesco_year": "1986"
    },
    "Sanchi Stupa": {
        "location": "Sanchi",
        "state": "Madhya Pradesh",
        "built_by": "Emperor Ashoka",
        "year_built": "3rd century BCE",
        "century": "3rd century BCE",
        "architectural_style": "Buddhist",
        "material": "Stone and brick",
        "religion": "Buddhist",
        "purpose": "Buddhist monument",
        "unesco_year": "1989"
    },
    "Golden Temple Amritsar": {
        "location": "Amritsar",
        "state": "Punjab",
        "built_by": "Guru Arjan Dev",
        "year_built": "1589-1604",
        "century": "16th-17th century",
        "architectural_style": "Sikh",
        "material": "Gold and marble",
        "religion": "Sikh",
        "purpose": "Gurdwara",
        "alternative_name": "Harmandir Sahib"
    },
    "Charminar Hyderabad": {
        "location": "Hyderabad",
        "state": "Telangana",
        "built_by": "Muhammad Quli Qutb Shah",
        "year_built": "1591",
        "century": "16th century",
        "architectural_style": "Indo-Islamic",
        "material": "Granite and lime mortar",
        "religion": "Islamic",
        "purpose": "Monument and mosque"
    },
    "Victoria Memorial Kolkata": {
        "location": "Kolkata",
        "state": "West Bengal",
        "built_by": "British Raj",
        "year_built": "1906-1921",
        "century": "20th century",
        "architectural_style": "Indo-Saracenic Revival",
        "material": "White marble",
        "religion": "Secular",
        "purpose": "Museum and memorial",
        "dedicated_to": "Queen Victoria"
    },
    "Hawa Mahal Jaipur": {
        "location": "Jaipur",
        "state": "Rajasthan",
        "built_by": "Maharaja Sawai Pratap Singh",
        "year_built": "1799",
        "century": "18th century",
        "architectural_style": "Rajput",
        "material": "Red and pink sandstone",
        "religion": "Hindu",
        "purpose": "Palace",
        "windows": "953 windows"
    }
}

# Question templates (8 types)
QUESTION_TEMPLATES = {
    "monument_identification": [
        "What is this monument?",
        "What monument is shown in the image?",
        "Name this monument.",
        "What is the name of this structure?",
        "Which monument is this?"
    ],
    "location": [
        "Where is this monument located?",
        "In which city is this monument?",
        "Where can you find this monument?",
        "What is the location of this monument?",
        "Which city is this monument in?"
    ],
    "state": [
        "In which state is this monument?",
        "Which Indian state has this monument?",
        "What state is this in?"
    ],
    "architectural_style": [
        "What is the architectural style of this monument?",
        "What type of architecture is this?",
        "What architectural style does this represent?",
        "What is the style of this structure?"
    ],
    "builder_patron": [
        "Who built this monument?",
        "Who commissioned this structure?",
        "Which ruler built this?",
        "Who was the patron of this monument?"
    ],
    "time_period": [
        "When was this built?",
        "In which century was this constructed?",
        "What is the time period of this monument?",
        "When was this monument constructed?"
    ],
    "material": [
        "What is the primary building material?",
        "What is this monument made of?",
        "What material was used to build this?",
        "What is the construction material?"
    ],
    "religion": [
        "What is the religious significance?",
        "Which religion is this associated with?",
        "What is the religious context of this monument?"
    ],
    "purpose": [
        "What was the purpose of this structure?",
        "What is this monument used for?",
        "Why was this built?"
    ]
}


class QAGenerator:
    """Generates question-answer pairs for heritage images"""
    
    def __init__(self):
        self.qa_pairs = []
        self.metadata = []
        
    def load_metadata(self):
        """Load consolidated metadata"""
        print("\n" + "="*60)
        print("📄 LOADING METADATA")
        print("="*60)
        
        if not METADATA_FILE.exists():
            print(f"❌ Metadata file not found: {METADATA_FILE}")
            print("   Please run audit_and_cleanup_fixed.py first!")
            return False
        
        with open(METADATA_FILE, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)
        
        print(f"✅ Loaded {len(self.metadata)} image records")
        print("="*60)
        return True
    
    def generate_qa_for_image(self, image_record):
        """Generate QA pairs for a single image"""
        
        image_id = image_record['image_id']
        filename = image_record['filename']
        monument_name = image_record['monument_category']
        
        # Get monument info
        monument_info = MONUMENT_INFO.get(monument_name, {})
        
        if not monument_info:
            print(f"⚠️  No info for {monument_name}, skipping {filename}")
            return []
        
        qa_pairs = []
        
        # Generate questions for each type
        question_types = [
            ("monument_identification", monument_name),
            ("location", monument_info.get("location", "Unknown")),
            ("state", monument_info.get("state", "Unknown")),
            ("architectural_style", monument_info.get("architectural_style", "Unknown")),
            ("builder_patron", monument_info.get("built_by", "Unknown")),
            ("time_period", monument_info.get("century", "Unknown")),
            ("material", monument_info.get("material", "Unknown")),
            ("religion", monument_info.get("religion", "Unknown")),
        ]
        
        for question_type, answer in question_types:
            # Skip if answer is unknown
            if answer == "Unknown":
                continue
            
            # Pick random question variant
            question_variants = QUESTION_TEMPLATES.get(question_type, [])
            if not question_variants:
                continue
            
            question = random.choice(question_variants)
            
            qa_pairs.append({
                "image_id": image_id,
                "filename": filename,
                "monument_category": monument_name,
                "question_id": f"{image_id}_q{len(qa_pairs) + 1}",
                "question": question,
                "answer": answer,
                "question_type": question_type,
                "confidence": 1.0,
                "source": "automated_generation"
            })
        
        return qa_pairs
    
    def generate_all_qa_pairs(self):
        """Generate QA pairs for all images"""
        print("\n" + "="*60)
        print("🤖 GENERATING QA PAIRS")
        print("="*60)
        
        monument_stats = {}
        
        for image_record in self.metadata:
            monument_name = image_record['monument_category']
            
            # Generate QA pairs
            qa_pairs = self.generate_qa_for_image(image_record)
            self.qa_pairs.extend(qa_pairs)
            
            # Track stats
            if monument_name not in monument_stats:
                monument_stats[monument_name] = {"images": 0, "qa_pairs": 0}
            
            monument_stats[monument_name]["images"] += 1
            monument_stats[monument_name]["qa_pairs"] += len(qa_pairs)
        
        print(f"\n✅ Generated {len(self.qa_pairs)} QA pairs")
        
        print("\n📊 QA pairs per monument:")
        print("-" * 60)
        for monument, stats in sorted(monument_stats.items()):
            avg = stats["qa_pairs"] / stats["images"] if stats["images"] > 0 else 0
            print(f"{monument:30s}: {stats['qa_pairs']:4d} QA pairs ({avg:.1f} per image)")
        print("-" * 60)
        print(f"TOTAL: {len(self.qa_pairs)} QA pairs")
        print("="*60)
    
    def save_annotations(self):
        """Save QA pairs to JSON and CSV"""
        print("\n" + "="*60)
        print("💾 SAVING ANNOTATIONS")
        print("="*60)
        
        # Create output directory
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Save full annotations (JSON)
        full_json = OUTPUT_DIR / "annotations.json"
        with open(full_json, 'w', encoding='utf-8') as f:
            json.dump(self.qa_pairs, f, indent=2, ensure_ascii=False)
        print(f"✅ JSON: {full_json}")
        
        # Save CSV (for easy viewing/editing)
        csv_file = OUTPUT_DIR / "annotations.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            if self.qa_pairs:
                fieldnames = list(self.qa_pairs[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.qa_pairs)
        print(f"✅ CSV: {csv_file}")
        
        # Save summary report
        summary_file = OUTPUT_DIR / "generation_report.txt"
        with open(summary_file, 'w') as f:
            f.write("QA GENERATION REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Total images: {len(self.metadata)}\n")
            f.write(f"Total QA pairs: {len(self.qa_pairs)}\n")
            f.write(f"Avg QA per image: {len(self.qa_pairs) / len(self.metadata):.1f}\n\n")
            
            # Per-monument breakdown
            f.write("QA PAIRS BY MONUMENT:\n")
            f.write("-" * 60 + "\n")
            monument_counts = {}
            for qa in self.qa_pairs:
                monument = qa['monument_category']
                monument_counts[monument] = monument_counts.get(monument, 0) + 1
            
            for monument, count in sorted(monument_counts.items()):
                f.write(f"{monument:30s}: {count:4d} QA pairs\n")
            f.write("-" * 60 + "\n")
            
            # Question type breakdown
            f.write("\nQA PAIRS BY QUESTION TYPE:\n")
            f.write("-" * 60 + "\n")
            type_counts = {}
            for qa in self.qa_pairs:
                qtype = qa['question_type']
                type_counts[qtype] = type_counts.get(qtype, 0) + 1
            
            for qtype, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(self.qa_pairs)) * 100
                f.write(f"{qtype:30s}: {count:4d} ({percentage:5.1f}%)\n")
            
        print(f"✅ Report: {summary_file}")
        
        print("="*60)
    
    def run(self):
        """Execute full QA generation pipeline"""
        print("\n" + "="*70)
        print(" " * 15 + "QA PAIR GENERATION")
        print("="*70)
        
        # Load metadata
        if not self.load_metadata():
            return
        
        # Generate QA pairs
        self.generate_all_qa_pairs()
        
        # Save everything
        self.save_annotations()
        
        print("\n" + "="*70)
        print("✅ QA GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📁 Outputs saved to: {OUTPUT_DIR.absolute()}")
        print("   - annotations.json (all QA pairs)")
        print("   - annotations.csv (for Excel/editing)")
        print("   - generation_report.txt (summary stats)")
        print("\n💡 Next Steps:")
        print("   1. Review annotations.csv in Excel")
        print("   2. Edit/refine questions if needed")
        print("   3. Ready for model training!")
        print("\n🎉 Your dataset is complete!")
        print("="*70 + "\n")


if __name__ == "__main__":
    # Set random seed for reproducibility
    random.seed(42)
    
    generator = QAGenerator()
    
    try:
        generator.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()