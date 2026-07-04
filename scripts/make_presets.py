"""Generate presets/*.txt job-description presets.

Two kinds:
- single presets:   presets/<category>--<slug>.txt
- leveled presets:  presets/<category>--<slug>--<level>.txt  (intern/junior/mid/senior)

Leveled roles are generated from one spec per role: shared core requirements,
plus advanced requirements that appear from mid level up, with level-appropriate
years/degree lines - mirroring how real postings scale by seniority.

The web app groups level variants under one picker entry with a level switch.
Wording deliberately uses terms from cvgrader/data/skills.json.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "presets"

# --------------------------------------------------------------- single presets
P = {}

P["software--it-support-specialist"] = """IT Support Specialist
Harborview Group - On-site

About the role
Be the first line of help for employees' hardware, software and account issues.

Requirements
- 1+ years in IT support or help desk
- Windows administration and Microsoft 365 / Office 365
- Ticketing systems (Zendesk, ServiceNow or similar)
- Networking basics: TCP/IP, DNS, VPN, firewalls
- Strong customer service and communication skills

Nice to have
- CompTIA A+ or Network+ certification
- Basic Linux experience
- Active Directory and IAM administration
- Hardware troubleshooting and asset management
"""

P["product-design--technical-writer"] = """Technical Writer
Quillstone Docs - Remote

About the role
Own developer-facing documentation for our API platform.

Requirements
- 2+ years of technical writing experience
- Documenting REST APIs and developer tools
- Ability to read code samples (Python or JavaScript)
- Git-based docs-as-code workflow
- Strong editing and information architecture skills

Nice to have
- Markdown static-site generators
- OpenAPI / Swagger specs
- Developer background
- Content strategy experience
"""

P["marketing--social-media-manager"] = """Social Media Manager
Juniper & Co - Remote

About the role
Own our voice and growth across Instagram, TikTok, LinkedIn and X.

Requirements
- 2+ years in social media management
- Content creation and content strategy for social channels
- Community management and engagement
- Analytics and reporting on growth and engagement KPIs
- Short-form video planning and copywriting

Nice to have
- Paid social campaigns (Meta Ads)
- Design tools (Photoshop or Figma)
- Influencer partnerships
- Brand management experience
"""

P["marketing--seo-specialist"] = """SEO Specialist
Rankwell Agency - Remote

About the role
Grow organic traffic for a portfolio of B2B and e-commerce clients.

Requirements
- 2+ years of hands-on SEO experience
- On-page, technical and off-page SEO
- Google Analytics and Search Console
- Content strategy and content marketing collaboration
- Competitive analysis and reporting

Nice to have
- Basic HTML understanding
- SEM / Google Ads
- Local SEO
- Marketing analytics dashboards (Looker Studio, Power BI)
"""

P["marketing--content-writer"] = """Content Writer
Fieldnote Media - Remote

About the role
Write articles, guides and landing pages that rank and convert.

Requirements
- 2+ years of content writing or copywriting
- SEO-aware writing and keyword integration
- Research-heavy long-form content
- Editing and proofreading to a style guide
- Managing a content calendar and deadlines

Nice to have
- Content marketing strategy
- Email marketing copy
- B2B or SaaS writing experience
- Basic Google Analytics
"""

P["sales-support--sales-development-rep"] = """Sales Development Representative (SDR)
Crestline Software - Hybrid

About the role
Open doors: prospect, qualify and book meetings for our account executives.

Requirements
- 1+ years in sales, lead generation or customer-facing work
- Cold calling and cold outreach (email, LinkedIn)
- Prospecting and lead qualification
- CRM hygiene (Salesforce or HubSpot)
- Resilience and quota-driven mindset

Nice to have
- B2B SaaS experience
- Sales engagement tooling
- Negotiation basics
- Bachelor's degree
"""

P["sales-support--account-executive"] = """Account Executive
Crestline Software - Hybrid

About the role
Own the full B2B sales cycle from discovery to close for mid-market accounts.

Requirements
- 2+ years of closing experience in B2B sales
- Consistent quota attainment
- Pipeline management in Salesforce
- Discovery, demo and negotiation skills
- Forecasting accuracy and CRM discipline

Nice to have
- SaaS sales experience
- Business development or partnership experience
- MEDDIC or similar methodology
- Bachelor's degree
"""

P["sales-support--account-manager"] = """Account Manager
Bridgeport Solutions - Hybrid

About the role
Grow and retain a book of existing B2B accounts.

Requirements
- 2+ years in account management or client-facing roles
- Building long-term client relationships
- Renewals, upsells and contract negotiation
- CRM usage (Salesforce or HubSpot)
- Cross-functional collaboration with product and support

Nice to have
- Customer success background
- Quota or revenue-retention targets
- Industry experience in logistics or SaaS
"""

P["sales-support--customer-success-manager"] = """Customer Success Manager
Lumen Desk - Remote

About the role
Make our customers successful from onboarding through renewal.

Requirements
- 2+ years in customer success or account management
- Onboarding, adoption and retention ownership
- Churn reduction and health-score monitoring
- CRM and CS tooling (Salesforce, HubSpot or similar)
- Excellent communication and stakeholder management

Nice to have
- SaaS experience
- Upsell / expansion motion
- Basic SQL or analytics
- Support or training background
"""

P["sales-support--customer-service-rep"] = """Customer Service Representative
Northgate Home Services - On-site

About the role
Help customers by phone, chat and email; resolve issues fast and kindly.

Requirements
- 1+ years in customer service or retail
- Ticketing systems (Zendesk or similar)
- Clear written and verbal communication
- Multitasking across channels with attention to detail
- Conflict resolution and patience

Nice to have
- CRM experience
- Bilingual ability
- Scheduling or dispatch experience
- Microsoft Office
"""

P["finance--staff-accountant"] = """Staff Accountant
Harlow & Finch LLP - On-site

About the role
Own the general ledger, reconciliations and month-end close support.

Requirements
- 2+ years of accounting experience
- General ledger, journal entries and reconciliation
- Accounts payable and accounts receivable
- GAAP knowledge
- QuickBooks, Xero or NetSuite
- Bachelor's degree in Accounting

Nice to have
- CPA or CPA progress
- Audit support experience
- Advanced Excel
- Payroll processing
"""

P["hr-operations--hr-generalist"] = """HR Generalist
Copperfield Manufacturing - On-site

About the role
Run day-to-day HR for a 200-person plant: onboarding to offboarding.

Requirements
- 2+ years in an HR role
- Onboarding, benefits administration and payroll coordination
- HRIS experience (Workday, ADP or similar)
- Employee relations and policy compliance
- Recruiting coordination and interview scheduling
- Confidentiality and attention to detail

Nice to have
- PHR / SHRM certification
- Training and development programs
- Union environment experience
"""

P["hr-operations--recruiter"] = """Recruiter
TalentBridge Partners - Hybrid

About the role
Run full-cycle recruiting for technology and operations roles.

Requirements
- 2+ years in recruiting or talent acquisition
- Full-cycle recruiting: sourcing candidates to offer negotiation
- ATS management and pipeline reporting
- Sourcing via LinkedIn and creative channels
- Strong communication and stakeholder management

Nice to have
- Technical recruiting experience
- Employer branding
- HRIS familiarity (Workday)
- Agency and in-house experience
"""

P["hr-operations--operations-manager"] = """Operations Manager
Beacon Fulfillment - On-site

About the role
Run daily operations for a 60-person fulfillment site.

Requirements
- 3+ years in operations management
- Process improvement and operational efficiency
- KPI ownership and performance reporting
- Team leadership: scheduling, coaching, hiring input
- Budgeting and cost control
- Cross-functional collaboration with supply chain

Nice to have
- Lean or Six Sigma
- ERP / WMS systems (SAP or NetSuite)
- Health and safety compliance
- Continuous improvement programs
"""

P["hr-operations--supply-chain-coordinator"] = """Supply Chain Coordinator
Pinewave Consumer Goods - Hybrid

About the role
Keep product flowing: POs, inventory, carriers and vendor follow-up.

Requirements
- 1+ years in supply chain, logistics or procurement
- Inventory management and purchase order processing
- Carrier and vendor coordination
- Excel for tracking and reporting
- Attention to detail under deadlines

Nice to have
- ERP experience (SAP, NetSuite)
- Demand planning / forecasting exposure
- Import/export documentation
- Warehouse operations familiarity
"""

P["hr-operations--administrative-assistant"] = """Administrative Assistant
Ashford Legal Group - On-site

About the role
Keep the office running: calendars, documents, travel and front-of-house.

Requirements
- 1+ years in administrative support
- Microsoft Office: Word, Excel, Outlook, PowerPoint
- Calendar management and scheduling
- Data entry with high accuracy
- Professional written and verbal communication
- Discretion with confidential information

Nice to have
- QuickBooks or expense tools
- Event coordination
- CRM data upkeep
- Notary or legal office experience
"""

P["health-education--registered-nurse"] = """Registered Nurse (Med-Surg)
St. Alban's Medical Center - On-site

About the role
Provide direct patient care on a 32-bed medical-surgical unit.

Requirements
- Active RN license in good standing
- 1+ years of clinical experience (new grads with strong clinicals considered)
- Patient care, assessment and care planning
- EMR documentation (Epic Systems preferred)
- BLS certification required; ACLS preferred
- BSN or Associate degree in Nursing

Nice to have
- Med-surg or telemetry experience
- Charge nurse or preceptor experience
- Wound care
"""

P["health-education--teacher"] = """Secondary School Teacher (Science)
Riverbend Academy - On-site

About the role
Teach general science and biology to grades 8-10 in a supportive school.

Requirements
- Bachelor's degree in Education or a science field
- Teaching license / certification (or eligibility)
- Lesson planning aligned to curriculum standards
- Classroom management for classes of 25-30
- Student assessment and progress reporting
- Parent and staff communication

Nice to have
- Curriculum design experience
- Technology-enhanced instruction (Google Classroom)
- Extracurricular coaching or club sponsorship
- Special education awareness
"""

# -------------------------------------------- academic, degrees & scholarships
P["academic--erasmus-mundus-masters"] = """Erasmus Mundus Joint Master Scholarship
European Commission funded programme - multiple EU universities

About the programme
Fully funded two-year joint master's degree studied in at least two European
countries. Selection is CV-based plus motivation letter; academic merit and
international outlook weigh heaviest.

Requirements
- Bachelor's degree in a relevant field (completed or final year)
- Strong academic record (GPA / distinction level grades)
- English proficiency: IELTS 6.5+ or TOEFL 90+ (or equivalent CEFR C1)
- Demonstrated motivation for the field of study
- Extracurricular or volunteering engagement

Nice to have
- Research experience or a thesis project
- International experience (exchange program, study abroad)
- Publications or conference presentations
- Second European language
- Scholarship or academic awards
"""

P["academic--erasmus-exchange-semester"] = """Erasmus+ Exchange Semester
Home university international office - partner universities across Europe

About the programme
One or two semesters abroad at a partner university with an Erasmus+ mobility
grant. Ranked on academic record and motivation.

Requirements
- Currently enrolled Bachelor's or Master's student
- Strong academic record (GPA above faculty threshold)
- English proficiency (B2 or higher; IELTS/TOEFL accepted)
- Motivation and study plan matching the host university
- Good standing with no outstanding course deficits

Nice to have
- Extracurricular involvement (student club, student council)
- Volunteering or community service
- Additional languages of the host country
- Prior international experience
"""

P["academic--research-lab-assistant-ai"] = """Research Assistant - AI/ML Lab
University Computer Science Department

About the position
Part-time research assistant supporting graduate research in machine learning.

Requirements
- Enrolled in or completed a Bachelor's in Computer Science or related field
- Strong Python; NumPy, Pandas and scikit-learn
- Machine learning fundamentals (coursework or projects)
- Ability to read papers and write a literature review
- Git for collaborative research code

Nice to have
- PyTorch or TensorFlow experience
- Research experience or publications
- LaTeX for paper writing
- Strong academic record (GPA, dean's list)
"""

P["academic--wet-lab-research-assistant"] = """Research Assistant - Molecular Biology Wet Lab
University Life Sciences Institute

About the position
Support ongoing research projects with hands-on bench work and data collection.

Requirements
- Bachelor's degree (or final year) in Biology, Biochemistry or related field
- Wet lab skills: PCR, cell culture, western blot or ELISA
- Accurate lab notebook keeping and aseptic technique
- Data analysis basics (Excel or R)
- Attention to detail and reliability

Nice to have
- Microscopy or chromatography experience
- Research experience beyond coursework
- Statistics coursework
- Poster presentation or publication
"""

P["academic--phd-position-stem"] = """PhD Position (STEM)
University Doctoral School - funded position

About the position
Fully funded doctoral position; selection weighs research potential above all.

Requirements
- Master's degree in a relevant STEM field
- Research experience with a completed thesis
- Academic writing ability (research proposal required)
- Statistics and data analysis competence
- English proficiency (IELTS/TOEFL if not native)

Nice to have
- Peer-reviewed publications or conference presentations
- LaTeX
- Teaching assistant or tutoring experience
- Research grant or scholarship history
- Programming (Python, R or MATLAB)
"""

P["academic--masters-program-cs"] = """M.S. in Computer Science - Admission
Graduate School of Engineering

About the programme
Two-year thesis-track master's. Admissions reviews CV, transcripts and statement.

Requirements
- Bachelor's degree in Computer Science or closely related field
- Strong academic record (GPA 3.0+/4.0 or equivalent)
- Programming proficiency (Python, Java or C++)
- Core CS coursework: algorithms, data structures, databases (SQL)
- English proficiency for international applicants (TOEFL/IELTS)

Nice to have
- GRE scores
- Research experience or publications
- Personal projects on GitHub
- Relevant internships
- Extracurricular or hackathon participation
"""

P["academic--mba-program"] = """MBA Programme - Admission
Graduate School of Business

About the programme
Full-time two-year MBA. Holistic review of CV, essays and test scores.

Requirements
- Bachelor's degree in any discipline
- 2+ years of professional work experience
- GMAT or GRE score
- Demonstrated leadership and career progression
- English proficiency for international applicants (TOEFL/IELTS)

Nice to have
- Team management or people management experience
- Quantitative skills: Excel, financial analysis, statistics
- Community service or volunteering
- International experience
- Entrepreneurial or business development track record
"""

P["academic--fulbright-scholarship"] = """Fulbright Foreign Student Scholarship
Binational Fulbright Commission

About the award
Fully funded graduate study in the United States. Selection emphasizes academic
merit, leadership and cultural ambassadorship.

Requirements
- Bachelor's degree with a strong academic record (GPA)
- English proficiency: TOEFL or IELTS at competitive scores
- Demonstrated leadership experience
- Community service or volunteering commitment
- Clear study/research objective in the chosen field

Nice to have
- Research experience or publications
- Teaching, tutoring or mentoring experience
- Extracurricular achievements and awards
- International or cross-cultural experience
"""

P["academic--daad-masters-scholarship"] = """DAAD Master's Scholarship (Germany)
German Academic Exchange Service

About the award
Funded master's study at a German university for international graduates.

Requirements
- Bachelor's degree with above-average academic record (GPA)
- Typically 2+ years since graduation with related work experience
- English proficiency (IELTS/TOEFL) for English-taught programmes
- Motivation aligned with development or research goals
- Academic references

Nice to have
- German language skills (B1/B2 or Goethe certificate)
- Research experience or publications
- Volunteering or community engagement
- Scholarship or academic awards history
"""

P["academic--university-teaching-assistant"] = """Undergraduate Teaching Assistant
University Department - semester contract

About the position
Support a core course: labs, office hours, grading and student questions.

Requirements
- Currently enrolled student in the department with strong academic record
- Completed the course (or equivalent) with top grades
- Tutoring, peer mentoring or teaching assistant experience preferred
- Reliable grading and progress reporting
- Clear communication and patience

Nice to have
- Lesson planning or workshop facilitation
- Experience with the course's tools (e.g. Python, MATLAB or lab equipment)
- Dean's list or academic awards
"""

P["academic--summer-research-internship"] = """Summer Research Internship (REU-style)
University Research Programme - 10 weeks, funded

About the programme
Paid summer research placement for undergraduates in STEM labs.

Requirements
- Enrolled undergraduate in a STEM field
- Strong academic record (GPA 3.0+)
- Coursework foundation relevant to the host lab
- Basic data analysis (Python, R, MATLAB or Excel)
- Motivation for research and graduate study

Nice to have
- Prior research experience or lab coursework
- Poster or oral presentation experience
- Programming projects on GitHub
- Statistics coursework
"""

# ------------------------------------------------------------- leveled roles
# Each spec: title, company/location, about, core reqs (all levels),
# advanced reqs (appear from mid level; senior gets all), nice-to-haves.
LEVEL_ORDER = ["intern", "junior", "mid", "senior"]
LEVEL_TITLES = {
    "intern": "{title} Intern",
    "junior": "Junior {title}",
    "mid": "{title}",
    "senior": "Senior {title}",
}
LEVEL_YEARS = {
    "intern": "Currently enrolled in a Bachelor's degree in a related field",
    "junior": "0-1 years of professional experience (internships and projects count)",
    "mid": "2-4 years of professional experience",
    "senior": "5+ years of professional experience",
}

ROLES = {
    "software--software-engineer": {
        "title": "Software Engineer (Backend)",
        "company": "Nimbus Analytics - Seattle, WA (Hybrid)",
        "about": "Design, build and scale the backend services behind our analytics platform.",
        "core": [
            "Strong programming in Python or Java",
            "SQL and relational databases (PostgreSQL or MySQL)",
            "Building REST APIs",
            "Git-based workflow",
        ],
        "advanced": [
            "Designing microservices architectures",
            "AWS or another cloud platform in production",
            "Docker and Kubernetes",
            "CI/CD pipelines (GitHub Actions or Jenkins)",
        ],
        "nth": ["GraphQL", "Kafka or event streaming", "Terraform / infrastructure-as-code"],
    },
    "software--frontend-developer": {
        "title": "Frontend Developer",
        "company": "Brightlane Apps - Remote",
        "about": "Build polished, accessible user interfaces for our B2B web products.",
        "core": [
            "Strong JavaScript and TypeScript",
            "React and modern state management (Redux or similar)",
            "HTML, CSS and responsive layout",
            "Consuming REST APIs or GraphQL",
        ],
        "advanced": [
            "Next.js or server-side rendering",
            "Testing with Jest, Cypress or Playwright",
            "Performance optimization and accessibility (WCAG)",
        ],
        "nth": ["Figma and design systems", "Node.js", "CI/CD familiarity"],
    },
    "software--fullstack-developer": {
        "title": "Full-Stack Developer",
        "company": "Everest Digital - Kathmandu, Nepal (Hybrid)",
        "about": "Own features end to end - database to UI - for client web applications.",
        "core": [
            "JavaScript and a modern framework (React, Vue or Angular)",
            "Backend with Node.js, Django or Spring",
            "SQL and relational database design (MySQL or PostgreSQL)",
            "REST API design and integration",
        ],
        "advanced": [
            "Docker and CI/CD",
            "Cloud deployment (AWS or similar)",
            "TypeScript across the stack",
        ],
        "nth": ["GraphQL", "UI/UX sensibility and Figma", "Testing (Jest or Pytest)"],
    },
    "software--mobile-developer": {
        "title": "Mobile Developer",
        "company": "Pocketworks Studio - Remote",
        "about": "Ship and maintain our consumer mobile apps on iOS and Android.",
        "core": [
            "Swift and iOS development, or Kotlin and Android",
            "REST APIs and offline data handling",
            "Git and code review workflow",
        ],
        "advanced": [
            "App Store / Play Store release ownership",
            "CI/CD for mobile builds",
            "Unit testing and UI test automation",
        ],
        "nth": ["React Native or Flutter", "Push notifications and analytics", "Performance profiling"],
    },
    "software--devops-engineer": {
        "title": "DevOps Engineer",
        "company": "Skyloft Systems - Remote",
        "about": "Own the reliability, automation and deployment pipeline of our cloud platform.",
        "core": [
            "Linux administration and shell scripting",
            "AWS fundamentals (EC2, S3, RDS)",
            "Docker",
            "CI/CD pipelines (GitHub Actions, GitLab CI or Jenkins)",
        ],
        "advanced": [
            "Kubernetes in production",
            "Terraform / infrastructure-as-code at scale",
            "Monitoring and observability (Prometheus, Grafana or Datadog)",
        ],
        "nth": ["Python or Go for tooling", "Ansible", "IAM and security best practices"],
    },
    "software--qa-engineer": {
        "title": "QA Engineer",
        "company": "Verity Labs - Remote",
        "about": "Build and maintain the automated test suites that guard our releases.",
        "core": [
            "Test planning and regression testing",
            "Test automation with Selenium, Cypress or Playwright",
            "API and integration testing",
            "Jira or similar tracking tools",
        ],
        "advanced": [
            "Test suites integrated into CI/CD pipelines",
            "Performance or load testing",
        ],
        "nth": ["JavaScript or Python scripting", "SQL for data validation", "Mobile app testing"],
    },
    "software--cybersecurity-analyst": {
        "title": "Cybersecurity Analyst",
        "company": "Sentinel Ridge Security - Hybrid",
        "about": "Monitor, detect and respond to threats across our clients' environments.",
        "core": [
            "Network security fundamentals: firewalls, VPN, DNS, TCP/IP",
            "Vulnerability management basics",
            "Security monitoring and log analysis",
        ],
        "advanced": [
            "SIEM operation (Splunk or similar) and incident response",
            "IAM, OAuth and SSO",
            "Compliance frameworks: SOC 2, ISO 27001 or HIPAA",
        ],
        "nth": ["Security+ or CISSP progress", "Python or PowerShell scripting", "Cloud security (AWS or Azure)"],
    },
    "software--cloud-architect": {
        "title": "Cloud Solutions Architect",
        "company": "Meridian Cloud Partners - Remote",
        "about": "Design secure, cost-effective cloud architectures for enterprise customers.",
        "levels": ["mid", "senior"],
        "core": [
            "Deep AWS experience; Azure or GCP a strong second",
            "Kubernetes, Docker and serverless architectures",
            "Terraform and infrastructure-as-code",
            "Networking, IAM and security best practices",
        ],
        "advanced": [
            "Architecture documentation and stakeholder communication",
            "Cost optimization / FinOps",
            "Migration projects from on-premise to cloud",
        ],
        "nth": ["AWS Certified Solutions Architect", "Multi-account governance", "Mentoring engineers"],
    },
    "data-ai--data-analyst": {
        "title": "Data Analyst",
        "company": "Corven Retail Group - Hybrid",
        "about": "Turn messy operational data into dashboards and decisions.",
        "core": [
            "Strong SQL for querying relational databases",
            "Excel including pivot tables and VLOOKUP",
            "Dashboards with Tableau, Power BI or Looker",
            "Statistics fundamentals",
        ],
        "advanced": [
            "Python (Pandas) for analysis",
            "A/B testing and experimentation",
            "Stakeholder reporting and data storytelling",
        ],
        "nth": ["Google Analytics", "dbt or data modeling exposure", "Retail or e-commerce domain experience"],
    },
    "data-ai--data-scientist": {
        "title": "Data Scientist",
        "company": "Halcyon Health Tech - Remote",
        "about": "Build models that predict patient outcomes and power product features.",
        "core": [
            "Python: Pandas, NumPy, scikit-learn",
            "Statistics and hypothesis testing",
            "SQL and working with production data",
            "Communicating findings to non-technical stakeholders",
        ],
        "advanced": [
            "A/B testing and experiment design at scale",
            "Deep learning with PyTorch or TensorFlow",
            "Partnering with engineering on model deployment",
        ],
        "nth": ["Spark or distributed processing", "LLMs or generative AI exposure", "Master's degree in a quantitative field"],
    },
    "data-ai--data-engineer": {
        "title": "Data Engineer",
        "company": "Northbeam Logistics - Hybrid",
        "about": "Build and operate the pipelines that feed our analytics and ML platforms.",
        "core": [
            "Strong SQL and Python",
            "ETL/ELT design and data warehousing concepts",
            "Airflow or similar orchestration",
        ],
        "advanced": [
            "Spark or other large-scale processing",
            "Snowflake, BigQuery or Redshift",
            "Data quality and observability tooling",
        ],
        "nth": ["dbt", "Kafka or event streaming", "Docker, Kubernetes and CI/CD"],
    },
    "data-ai--machine-learning-engineer": {
        "title": "Machine Learning Engineer",
        "company": "Arclight AI - Remote",
        "about": "Take models from notebook to production and keep them healthy at scale.",
        "core": [
            "Strong Python and software engineering fundamentals",
            "Machine learning fundamentals (scikit-learn, Pandas, NumPy)",
            "SQL",
        ],
        "advanced": [
            "PyTorch or TensorFlow in production",
            "Model deployment: Docker, Kubernetes, REST APIs",
            "Data pipelines and feature engineering",
        ],
        "nth": ["LLMs, RAG or generative AI systems", "MLOps and CI/CD for models", "Spark or distributed training"],
    },
    "product-design--product-manager": {
        "title": "Product Manager",
        "company": "Fernwood Software - Hybrid",
        "about": "Own the roadmap for our SMB invoicing product from discovery to launch.",
        "titles": {"intern": "Product Management Intern", "junior": "Associate Product Manager"},
        "core": [
            "User research and data-driven decision making",
            "Agile delivery with engineering teams (Scrum, Jira)",
            "Clear written communication and stakeholder management",
        ],
        "advanced": [
            "Roadmap ownership and product strategy",
            "Defining and tracking OKRs / KPIs",
            "Cross-functional leadership across sales, support and engineering",
        ],
        "nth": ["SQL or analytics self-service (Google Analytics, Looker)", "Technical background or CS degree", "B2B SaaS experience"],
    },
    "product-design--ux-designer": {
        "title": "UX Designer",
        "company": "Loomfield Studio - Remote",
        "about": "Design intuitive flows for our consumer finance app, from research to handoff.",
        "core": [
            "Figma proficiency including components and prototyping",
            "Wireframing, user flows and interaction design",
            "User research and usability testing",
        ],
        "advanced": [
            "Design system contribution",
            "Accessibility (WCAG) expertise",
            "Portfolio of shipped product work",
        ],
        "nth": ["Basic HTML/CSS understanding", "Motion design", "UX writing"],
    },
    "product-design--graphic-designer": {
        "title": "Graphic Designer",
        "company": "Copperleaf Creative - Hybrid",
        "about": "Produce brand, campaign and social assets for consumer clients.",
        "core": [
            "Photoshop, Illustrator and InDesign",
            "Layout design and typography",
            "Preparing print-ready and digital assets",
        ],
        "advanced": [
            "Brand identity systems",
            "Client presentation skills",
        ],
        "nth": ["Figma", "Motion graphics (After Effects)", "Photography and retouching"],
    },
    "marketing--digital-marketing-specialist": {
        "title": "Digital Marketing Specialist",
        "company": "Tidewater Brands - Hybrid",
        "about": "Run multi-channel campaigns for our direct-to-consumer product lines.",
        "titles": {"senior": "Digital Marketing Manager"},
        "core": [
            "Paid search and paid social: Google Ads, Meta Ads",
            "Google Analytics (GA4) and campaign reporting",
            "Email marketing (Mailchimp, Klaviyo or similar)",
            "SEO fundamentals and content marketing",
        ],
        "advanced": [
            "Budget ownership across channels",
            "A/B testing of landing pages",
            "Marketing automation (HubSpot)",
        ],
        "nth": ["Copywriting skills", "E-commerce experience", "Social media management"],
    },
    "finance--financial-analyst": {
        "title": "Financial Analyst",
        "company": "Granite Peak Capital - Hybrid",
        "about": "Own budgeting, forecasting and monthly reporting for two business units.",
        "core": [
            "Advanced Excel: financial modeling, pivot tables",
            "Forecasting, budgeting and variance analysis",
            "Financial reporting and month-end support",
        ],
        "advanced": [
            "ERP experience (SAP, NetSuite or Oracle)",
            "SQL or Power BI",
            "Valuation / DCF modeling",
        ],
        "nth": ["CFA progress", "Presentation skills for leadership reviews", "Bachelor's degree in Finance or Accounting"],
    },
    "hr-operations--project-manager": {
        "title": "Project Manager",
        "company": "Ironbridge Consulting - Hybrid",
        "about": "Deliver client projects on time and on budget across mixed teams.",
        "levels": ["mid", "senior"],
        "core": [
            "Project planning, scheduling and budgeting",
            "Agile and waterfall delivery; Scrum ceremonies",
            "Jira, Confluence and MS Project",
            "Risk management and status reporting",
        ],
        "advanced": [
            "Stakeholder management up to executive level",
            "Vendor management",
            "Change management",
        ],
        "nth": ["PMP or Certified Scrum Master", "Software delivery background", "Programme/portfolio exposure"],
    },
}


def build_leveled(key: str, spec: dict) -> dict:
    out = {}
    for level in spec.get("levels", LEVEL_ORDER):
        title = (spec.get("titles") or {}).get(level) or LEVEL_TITLES[level].format(title=spec["title"])
        reqs = [LEVEL_YEARS[level]]
        if level == "junior":
            reqs.append("Bachelor's degree or equivalent practical experience")
        reqs += spec["core"]
        if level == "mid":
            reqs += spec["advanced"][:2]
            reqs.append("Bachelor's degree in a related field or equivalent experience")
        elif level == "senior":
            reqs += spec["advanced"]
        nth = list(spec["nth"])
        if level == "intern":
            reqs.append("Coursework and personal projects count as experience")
            nth = ["Prior internship or part-time experience"] + nth[:2]
        elif level == "senior":
            nth.append("Mentoring and technical/team leadership")
        body = [title, spec["company"], "", "About the role", spec["about"], "", "Requirements"]
        body += [f"- {r}" for r in reqs]
        body += ["", "Nice to have"] + [f"- {n}" for n in nth]
        out[f"{key}--{level}"] = "\n".join(body) + "\n"
    return out


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.txt"):
        old.unlink()
    all_presets = dict(P)
    for key, spec in ROLES.items():
        all_presets.update(build_leveled(key, spec))
    for key, text in all_presets.items():
        (OUT / f"{key}.txt").write_text(text, encoding="utf-8")
    n_leveled = sum(len(s.get("levels", LEVEL_ORDER)) for s in ROLES.values())
    print(f"wrote {len(all_presets)} preset files "
          f"({len(P)} single + {n_leveled} level variants of {len(ROLES)} roles) to {OUT}")


if __name__ == "__main__":
    main()
