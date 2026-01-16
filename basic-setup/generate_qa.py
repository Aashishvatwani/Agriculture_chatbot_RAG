#!/usr/bin/env python3
"""
generate_qa.py

Generate random question-answer pairs for agriculture (soil & crops).

Usage:
  python generate_qa.py --count 100 --input files/agriculture_questions_1000.csv --output files/generated_qa.csv --seed 42

The script reads a CSV with a header `question` and produces a CSV with columns:
  question, answer, crop, topic

Answers are generated from simple templates and heuristics (no external APIs required).
"""
import csv
import random
import argparse
import re
from pathlib import Path

CROP_KEYWORDS = [
    'rice','wheat','maize','corn','soybean','cotton','potato','tomato','onion','garlic',
    'banana','sugarcane','barley','sorghum','millet','pulse','pea','lentil','millet',
    'potato','apple','grape','banana','tea','coffee'
]

SOIL_TOPICS = [
    'soil pH','nitrogen levels','phosphorus levels','potassium levels','organic matter',
    'soil texture','soil moisture','drainage','salinity','soil compaction'
]

# General definitions to append at the end of generated QA files
DEFINITIONS = [
    {
        'question': 'What is soil?',
        'answer': 'Soil is the upper layer of earth in which plants grow; it is a mixture of organic matter, minerals, gases, liquids, and organisms that together support life.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is irrigation?',
        'answer': 'Irrigation is the artificial application of water to the soil or land to assist in the growing of crops and vegetation when rainfall is insufficient.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is fertilizer?',
        'answer': 'Fertilizer is any material of natural or synthetic origin that is applied to soils or plant tissues to supply one or more plant nutrients essential to the growth of plants.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is pesticide?',
        'answer': 'A pesticide is a substance or mixture intended to prevent, destroy, repel or control pests, including insects, weeds, fungi, or other organisms harmful to crops.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is crop rotation?',
        'answer': 'Crop rotation is the practice of growing different types of crops in the same area in sequential seasons to improve soil health, optimize nutrients, and combat pests and diseases.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is integrated pest management (IPM)?',
        'answer': 'Integrated Pest Management (IPM) is an ecosystem-based strategy that focuses on long-term prevention of pests through a combination of techniques such as biological control, habitat manipulation, and use of resistant varieties.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is compost?',
        'answer': 'Compost is decomposed organic matter used as a soil amendment to improve soil structure, provide nutrients, and increase microbial activity.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is soil pH?',
        'answer': 'Soil pH measures the acidity or alkalinity of the soil on a scale from 0 to 14; most crops prefer slightly acidic to neutral soils (pH 6.0–7.5).',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is seed germination?',
        'answer': 'Seed germination is the process by which a seed emerges from dormancy and begins to sprout and grow into a seedling under favorable environmental conditions.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is post-harvest handling?',
        'answer': 'Post-harvest handling includes all operations and processes applied to crops from harvest to consumption, such as drying, cleaning, storage, packaging, and transportation to reduce losses and maintain quality.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is salinity in soils?',
        'answer': 'Soil salinity refers to the presence of high concentrations of soluble salts in soil, which can reduce plant growth by affecting water uptake and causing ion toxicity.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is organic matter in soil?',
        'answer': 'Soil organic matter consists of plant and animal residues at various stages of decomposition and is important for nutrient supply, water retention, and soil structure.',
        'crop': '',
        'topic': 'definition'
    },
    {
        'question': 'What is a soil test?',
        'answer': 'A soil test analyzes nutrient levels, pH, and other properties in a soil sample to guide fertilizer and amendment recommendations for optimal crop production.',
        'crop': '',
        'topic': 'definition'
    }
]

# Templates and helper lists for synthesizing additional questions when needed
QUESTION_TEMPLATES = [
    'How do I determine the optimal planting time for {crop} in {region}?',
    'What are the best seed varieties of {crop} for high yield and disease resistance in {region}?',
    'Which soil types are most suitable for cultivating {crop}?',
    'How can I test soil fertility before planting {crop}?',
    'What are the common pests of {crop} and how to control them?',
    'What are the symptoms of nutrient deficiency in {crop} and how to address them?',
    'How should I irrigate {crop} to maximize water efficiency?',
    'What are recommended spacing and plant density for {crop}?',
    'How do I manage weeds in {crop} fields effectively?',
    'What are post-harvest storage best practices for {crop}?',
    'How can I improve seed germination rates for {crop}?',
    'What are effective organic practices for growing {crop}?',
    'How do I diagnose fungal diseases in {crop} and treat them?',
    'What fertilizer program should I follow for a healthy {crop} crop?',
    'How do I prepare a soil bed for transplanting {crop} seedlings?',
    'What integrated pest management (IPM) strategies work well for {crop}?',
    'What are harvesting indicators that show {crop} is ready to harvest?',
    'How can I increase {crop} yield on smallholder farms?',
    'How to manage salinity or alkalinity issues when growing {crop}?',
    'How to reduce fertilizer runoff from {crop} fields and protect water quality?',
    'How do I select disease-resistant {crop} varieties for my area?',
    'What mechanization options are suitable for {crop} on medium farms?',
    'How to build a simple storage facility to store {crop} after harvest?',
    'What cover crops complement {crop} in rotation to improve soil health?',
    'How can I monitor {crop} health using drones or remote sensing?',
    'What are common post-harvest pests affecting {crop} and how to prevent them?',
    'How do I manage irrigation scheduling for {crop} during drought?',
    'What are recommended planting depths and sowing rates for {crop}?',
    'How to control bacterial diseases in {crop} crops?',
    'What are the profitable value-added products from {crop} processing?',
    'How can I use compost and organic amendments for {crop} production?',
    'What government schemes support {crop} farmers and how to apply?',
    'How do I identify nematode damage in {crop} and manage it?',
    'What are early warning signs of pest outbreaks in {crop} fields?',
    'How to manage post-harvest quality and grading for {crop}?',
    'How to establish a nursery for {crop} seedlings?',
    'What are water-saving irrigation techniques suitable for {crop}?',
    'How to select appropriate fertilizer blends for {crop}?',
    'How to perform a quick on-field soil test for {crop} planting?'
]

REGIONS = ['my region', 'tropical areas', 'temperate regions', 'arid zones', 'coastal areas', 'high-altitude areas']
PESTS = ['aphids','stem borers','cutworms','armyworms','weevils','mites','thrips','whiteflies','locusts']
SOIL_ISSUES = ['low nitrogen','low phosphorus','low potassium','high salinity','poor drainage','compaction','low organic matter']

def synthesize_questions(count, existing=None):
    """Synthesize `count` unique questions using templates, crops and helper lists.

    existing: iterable of questions to avoid duplicating
    """
    existing_set = set(q.strip().lower() for q in (existing or []))
    out = []
    tries = 0
    max_tries = count * 20

    while len(out) < count and tries < max_tries:
        tries += 1
        tmpl = random.choice(QUESTION_TEMPLATES)
        crop = random.choice(CROP_KEYWORDS)
        region = random.choice(REGIONS)
        pest = random.choice(PESTS)
        soil = random.choice(SOIL_ISSUES)

        # Replace placeholders that may appear in templates
        q = tmpl.format(crop=crop, region=region, pest=pest, soil=soil)

        # Small variations
        if random.random() < 0.12:
            q = 'How can I improve ' + q[0].lower() + q[1:]

        normalized = q.strip().lower()
        if normalized in existing_set or normalized in (s.lower() for s in out):
            continue

        out.append(q)

    if len(out) < count:
        print(f"Warning: only synthesized {len(out)} unique questions (requested {count}).")

    return out


def load_questions(csv_path):
    questions = []
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row.get('question') or row.get('Question') or ''
            q = q.strip()
            if q:
                questions.append(q)
    return questions

def detect_crop(question):
    q = question.lower()
    for crop in CROP_KEYWORDS:
        if re.search(r'\b' + re.escape(crop) + r's?\b', q):
            return crop
    return None

def detect_topic(question):
    q = question.lower()
    if any(word in q for word in ['soil', 'ph', 'nitrogen', 'phosphorus', 'potassium', 'organic']):
        return 'soil'
    if any(word in q for word in ['pest', 'disease', 'weed', 'ipm', 'fungus', 'bacteria', 'virus']):
        return 'pest/disease'
    if any(word in q for word in ['irrigat', 'water', 'drought', 'drainage']):
        return 'irrigation'
    if any(word in q for word in ['harvest', 'storage', 'post-harvest', 'yield']):
        return 'post-harvest'
    return 'general'

def random_soil_recommendation():
    ph = random.choice(['acidic (pH 5.5-6.5)', 'neutral (pH 6.5-7.5)', 'alkaline (pH 7.5+)'])
    n = random.choice(['low', 'medium', 'high'])
    p = random.choice(['low', 'medium', 'high'])
    k = random.choice(['low', 'medium', 'high'])
    return f"Soil appears {ph}. Recommended N-P-K levels: N={n}, P={p}, K={k}. Add organic matter and consider liming if acidic."

def generate_answer(question):
    crop = detect_crop(question)
    topic = detect_topic(question)

    if topic == 'soil':
        answer = (
            f"Soil advice: {random_soil_recommendation()} "
            "Perform a soil test for exact fertilizer recommendations; use compost to improve organic matter."
        )
    elif topic == 'pest/disease':
        answer = (
            "Pest/Disease guidance: Inspect plants for symptoms (spots, wilting, yellowing). "
            "Use integrated pest management (IPM): crop rotation, resistant varieties, targeted biocontrols, and correct pesticide application. "
            "If unsure, collect a sample and consult local extension services."
        )
    elif topic == 'irrigation':
        answer = (
            "Irrigation guidance: Water based on crop stage—establishment, vegetative growth, and reproductive stages need careful scheduling. "
            "Avoid waterlogging; use mulch to conserve moisture and consider drip irrigation for efficiency."
        )
    elif topic == 'post-harvest':
        answer = (
            "Post-harvest: Harvest at physiological maturity, dry to safe moisture content, and store in a cool, dry place to avoid pests. "
            "Use proper packaging and consider value-added processing to increase shelf life."
        )
    else:
        if crop:
            answer = (
                f"For {crop.capitalize()}: Follow certified seed, appropriate plant spacing, monitor for pests, and conduct soil tests. "
                "Apply balanced fertilizer based on soil test results and follow recommended irrigation schedules for the crop."
            )
        else:
            answer = (
                "General agronomy tip: Start with a soil test, choose locally adapted varieties, follow integrated pest management, "
                "and keep records of planting dates, inputs, and yields for continuous improvement."
            )

    # Add an actionable bullet or tip
    tip = random.choice([
        'Apply compost or well-rotted manure annually to improve soil structure.',
        'Rotate crops to reduce pest and disease pressure.',
        'Use certified seed and treat seeds where appropriate to reduce seed-borne diseases.',
        'Monitor fields weekly during critical growth stages for early pest detection.',
        'Test soil every 2-3 years and follow recommended fertilizer programs.'
    ])

    full_answer = f"{answer} Tip: {tip}"
    return full_answer, crop, topic

def write_output(rows, out_path):
    fieldnames = ['question','answer','crop','topic']
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def main():
    parser = argparse.ArgumentParser(description='Generate QA pairs for agriculture topics')
    parser.add_argument('--count', type=int, default=10000, help='Number of QA pairs to generate')
    parser.add_argument('--input', type=str, default='files/generated_qa_1000.csv', help='Input CSV with question column')
    parser.add_argument('--output', type=str, default='files/generated_qa.csv', help='Output CSV path')
    parser.add_argument('--seed', type=int, default=None, help='Random seed')
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    input_path = Path(__file__).resolve().parent / args.input
    output_path = Path(__file__).resolve().parent / args.output

    if not input_path.exists():
        print(f"Input file not found: {input_path}")
        return

    questions = load_questions(input_path)
    if not questions:
        print('No questions found in input file.')
        return

    selected = random.sample(questions, min(args.count, len(questions)))

    # If input CSV doesn't contain enough questions, synthesize more from templates
    if len(selected) < args.count:
        needed = args.count - len(selected)
        print(f"Synthesizing {needed} additional questions from templates...")
        synth = synthesize_questions(needed, existing=questions)
        selected.extend(synth)

    rows = []
    for q in selected:
        ans, crop, topic = generate_answer(q)
        rows.append({'question': q, 'answer': ans, 'crop': crop or '', 'topic': topic})

    # Append general definitions at the end of the generated QA output
    for d in DEFINITIONS:
        rows.append({
            'question': d['question'],
            'answer': d['answer'],
            'crop': d.get('crop', ''),
            'topic': d.get('topic', 'definition')
        })

    write_output(rows, output_path)
    print(f'Generated {len(rows)} QA pairs to {output_path}')

if __name__ == '__main__':
    main()
