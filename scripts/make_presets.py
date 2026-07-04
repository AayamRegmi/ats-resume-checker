"""Generate presets/<category>--<slug>.txt job-description presets.

These feed the web app's "sample job" dropdown (embedded into docs/data.js by
build_web_data.py) and can also be used with the CLI:  cvgrader cv.pdf --jd presets/...

Wording deliberately uses terms from cvgrader/data/skills.json so keyword
matching behaves the way it would on a real posting.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "presets"

P = {}

# ------------------------------------------------------------- software & IT
P["software--junior-software-engineer"] = """Junior Software Engineer
Bluepine Technologies - Remote

About the role
Help build and maintain our web platform and internal APIs alongside senior engineers.

Requirements
- Bachelor's degree in Computer Science or equivalent practical experience
- Solid programming fundamentals in Python or Java
- Understanding of SQL and relational databases (PostgreSQL or MySQL)
- Familiarity with Git and version control workflows
- Experience building REST APIs (coursework or personal projects count)
- Basic knowledge of HTML, CSS and JavaScript

Nice to have
- Internship or work experience in software development
- Exposure to Docker or cloud platforms (AWS, Azure or GCP)
- React or another modern frontend framework
- Unit testing experience (Pytest, JUnit or similar)
"""

P["software--senior-backend-engineer"] = """Senior Backend Engineer
Nimbus Analytics - Seattle, WA (Hybrid)

About the role
Design, build and scale the backend services behind our analytics platform.

Requirements
- 5+ years of professional software engineering experience
- Strong Python and SQL skills
- Experience designing microservices and REST APIs
- Hands-on with AWS (Lambda, ECS or EKS)
- Docker and Kubernetes in production
- CI/CD pipelines (GitHub Actions, Jenkins or similar)
- PostgreSQL or a similar relational database
- Bachelor's degree in Computer Science or a related field

Nice to have
- Terraform or other infrastructure-as-code tooling
- Kafka or other event streaming platforms
- GraphQL
- Experience mentoring engineers
"""

P["software--frontend-developer"] = """Frontend Developer
Brightlane Apps - Remote

About the role
Build polished, accessible user interfaces for our B2B web products.

Requirements
- 2+ years building production web applications
- Strong JavaScript and TypeScript
- React and modern state management (Redux or similar)
- HTML, CSS and responsive layout skills
- Experience consuming REST APIs or GraphQL
- Git-based workflow and code review culture

Nice to have
- Next.js or server-side rendering experience
- Accessibility (WCAG) knowledge
- Testing with Jest, Cypress or Playwright
- Familiarity with Figma and design systems
"""

P["software--fullstack-developer"] = """Full-Stack Web Developer
Everest Digital - Kathmandu, Nepal (Hybrid)

About the role
Own features end to end - database to UI - for client web applications.

Requirements
- 1+ years of experience building web applications (internships and freelance count)
- JavaScript and at least one modern framework (React, Vue or Angular)
- Backend experience with Node.js, Django, Laravel or Spring
- SQL and relational database design (MySQL or PostgreSQL)
- REST API design and integration
- Git-based workflow

Nice to have
- TypeScript
- Docker and basic CI/CD
- Experience deploying to AWS or a similar cloud
- UI/UX sensibility and familiarity with Figma
"""

P["software--mobile-developer"] = """Mobile Developer
Pocketworks Studio - Remote

About the role
Ship and maintain our consumer mobile apps on iOS and Android.

Requirements
- 2+ years of mobile development experience
- Swift and iOS development, or Kotlin and Android
- Experience with REST APIs and offline data handling
- App Store / Play Store release experience
- Git and code review workflow

Nice to have
- React Native or Flutter
- Unit testing and UI test automation
- CI/CD for mobile builds
- Push notifications and analytics integration
"""

P["software--devops-engineer"] = """DevOps Engineer
Skyloft Systems - Remote

About the role
Own the reliability, automation and deployment pipeline of our cloud platform.

Requirements
- 3+ years in DevOps, SRE or platform engineering
- Strong AWS experience (EC2, S3, Lambda, RDS)
- Docker and Kubernetes in production
- Terraform or other infrastructure-as-code
- CI/CD pipelines (GitHub Actions, GitLab CI or Jenkins)
- Linux administration and shell scripting
- Monitoring and observability (Prometheus, Grafana or Datadog)

Nice to have
- Python or Go for tooling
- Ansible configuration management
- Cost optimization experience
- Security and IAM best practices
"""

P["software--qa-engineer"] = """QA Automation Engineer
Verity Labs - Remote

About the role
Build and maintain the automated test suites that guard our releases.

Requirements
- 2+ years in quality assurance or test automation
- Test automation with Selenium, Cypress or Playwright
- API testing and integration testing experience
- Writing test plans and regression testing
- Jira or similar tracking tools
- Basic SQL for data validation

Nice to have
- JavaScript or Python scripting
- CI/CD pipeline integration of test suites
- Performance or load testing
- Mobile app testing
"""

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

P["software--cybersecurity-analyst"] = """Cybersecurity Analyst
Sentinel Ridge Security - Hybrid

About the role
Monitor, detect and respond to threats across our clients' environments.

Requirements
- 2+ years in information security or a SOC role
- SIEM experience (Splunk or similar) and incident response
- Vulnerability management and threat detection
- Network security fundamentals: firewalls, VPN, DNS, TCP/IP
- Understanding of IAM, OAuth and SSO concepts
- Bachelor's degree in a related field or equivalent experience

Nice to have
- Security+ / CISSP or working toward certification
- Compliance frameworks: SOC 2, ISO 27001, HIPAA or PCI DSS
- Scripting in Python or PowerShell
- Cloud security (AWS or Azure)
"""

P["software--cloud-architect"] = """Cloud Solutions Architect
Meridian Cloud Partners - Remote

About the role
Design secure, cost-effective cloud architectures for enterprise customers.

Requirements
- 5+ years in cloud engineering or architecture
- Deep AWS experience; Azure or GCP a strong second
- Kubernetes, Docker and serverless architectures
- Terraform and infrastructure-as-code at scale
- Networking, IAM and security best practices
- Stakeholder communication and architecture documentation

Nice to have
- AWS Certified Solutions Architect
- Cost optimization and FinOps experience
- Migration projects from on-premise to cloud
- Mentoring or team leadership
"""

# ---------------------------------------------------------------- data & AI
P["data-ai--data-analyst"] = """Data Analyst
Corven Retail Group - Hybrid

About the role
Turn messy operational data into dashboards and decisions for merchandising and ops.

Requirements
- 1+ years in an analyst role (internships count)
- Strong SQL for querying relational databases
- Excel including pivot tables and VLOOKUP
- Dashboarding with Tableau, Power BI or Looker
- Statistics fundamentals and data analysis rigor
- Clear written and verbal communication

Nice to have
- Python (Pandas) for analysis
- A/B testing or experimentation exposure
- Google Analytics
- Bachelor's degree in a quantitative field
"""

P["data-ai--data-scientist"] = """Data Scientist
Halcyon Health Tech - Remote

About the role
Build models that predict patient outcomes and power product features.

Requirements
- 2+ years in data science or applied ML
- Strong Python: Pandas, NumPy, scikit-learn
- Statistics, hypothesis testing and A/B testing
- SQL and working with production data
- Communicating findings to non-technical stakeholders
- Master's degree or Bachelor's with strong project portfolio

Nice to have
- Deep learning with PyTorch or TensorFlow
- Spark or distributed data processing
- Experiment design at scale
- Domain experience in healthcare
"""

P["data-ai--data-engineer"] = """Data Engineer
Northbeam Logistics - Hybrid

About the role
Build and operate the pipelines that feed our analytics and ML platforms.

Requirements
- 2+ years building data pipelines in production
- Strong SQL and Python
- ETL/ELT design and data warehousing concepts
- Airflow or similar orchestration
- Spark or other large-scale processing
- Snowflake, BigQuery or Redshift experience

Nice to have
- dbt
- Kafka or event streaming
- Docker, Kubernetes and CI/CD
- Data quality and observability tooling
"""

P["data-ai--machine-learning-engineer"] = """Machine Learning Engineer
Arclight AI - Remote

About the role
Take models from notebook to production and keep them healthy at scale.

Requirements
- 3+ years in ML engineering or backend engineering with ML exposure
- Strong Python and software engineering fundamentals
- PyTorch or TensorFlow in production
- Model deployment: Docker, Kubernetes, REST APIs
- Data pipelines and feature engineering
- SQL and cloud experience (AWS or GCP)

Nice to have
- LLMs, RAG or generative AI systems
- MLOps tooling and CI/CD for models
- Spark or distributed training
- NLP or computer vision background
"""

P["data-ai--ml-intern"] = """Machine Learning Intern
Kritim AI Labs - Kathmandu / Remote

About the role
Join our applied ML team for a 6-month internship building and evaluating
models for document understanding and NLP products.

Requirements
- Pursuing or recently completed a Bachelor's degree in Computer Science,
  Mathematics or a related field
- Strong Python skills
- Hands-on machine learning fundamentals (coursework, research or projects)
- Experience with NumPy, Pandas and scikit-learn
- Familiarity with PyTorch or TensorFlow
- Understanding of statistics and model evaluation

Nice to have
- NLP or computer vision project experience
- Published research or a public portfolio (GitHub, Kaggle)
- SQL
- Exposure to LLMs or generative AI
"""

# ---------------------------------------------------------- product & design
P["product-design--product-manager"] = """Product Manager
Fernwood Software - Hybrid

About the role
Own the roadmap for our SMB invoicing product from discovery to launch.

Requirements
- 3+ years in product management
- Roadmap ownership and product strategy
- User research and data-driven decision making
- Agile delivery with engineering teams (Scrum, Jira)
- Stakeholder management across sales, support and engineering
- Defining and tracking OKRs / KPIs

Nice to have
- SQL or analytics self-service (Google Analytics, Looker)
- Technical background or CS degree
- B2B SaaS experience
- Pricing and packaging exposure
"""

P["product-design--ux-designer"] = """UX Designer
Loomfield Studio - Remote

About the role
Design intuitive flows for our consumer finance app, from research to handoff.

Requirements
- 2+ years in UX or product design
- Figma proficiency including components and prototyping
- User research and usability testing
- Wireframing, user flows and interaction design
- Working within and contributing to design systems
- Portfolio demonstrating shipped work

Nice to have
- Accessibility (WCAG) expertise
- Basic HTML/CSS understanding
- Motion design
- UX writing
"""

P["product-design--graphic-designer"] = """Graphic Designer
Copperleaf Creative - Hybrid

About the role
Produce brand, campaign and social assets for a roster of consumer clients.

Requirements
- 2+ years of graphic design experience
- Expert Photoshop, Illustrator and InDesign
- Brand identity and layout design
- Preparing print-ready and digital assets
- Managing multiple deadlines with attention to detail

Nice to have
- Figma
- Motion graphics (After Effects, Premiere Pro)
- Photography or retouching
- Social media content formats
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

# ------------------------------------------------------------------ marketing
P["marketing--digital-marketing-specialist"] = """Digital Marketing Specialist
Tidewater Brands - Hybrid

About the role
Run multi-channel campaigns for our direct-to-consumer product lines.

Requirements
- 2+ years in digital marketing
- Paid search and paid social: Google Ads, Meta Ads
- Google Analytics (GA4) and campaign reporting
- Email marketing (Mailchimp, Klaviyo or similar)
- SEO fundamentals and content marketing
- Budget management across channels

Nice to have
- HubSpot or marketing automation
- Copywriting skills
- A/B testing of landing pages
- E-commerce experience
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

# ------------------------------------------------------------ sales & support
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

# --------------------------------------------------------------------- finance
P["finance--financial-analyst"] = """Financial Analyst
Granite Peak Capital - Hybrid

About the role
Own budgeting, forecasting and monthly reporting for two business units.

Requirements
- 2+ years in FP&A, financial analysis or accounting
- Advanced Excel: financial modeling, pivot tables
- Forecasting, budgeting and variance analysis
- Financial reporting and month-end support
- Bachelor's degree in Finance, Accounting or Economics

Nice to have
- SQL or Power BI
- ERP experience (SAP, NetSuite or Oracle)
- CFA progress
- Valuation / DCF modeling
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

# ------------------------------------------------------------ HR, ops & admin
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

P["hr-operations--project-manager"] = """Project Manager
Ironbridge Consulting - Hybrid

About the role
Deliver client projects on time and on budget across mixed teams.

Requirements
- 3+ years of project management experience
- Project planning, scheduling and budgeting
- Agile and waterfall delivery; Scrum ceremonies
- Jira, Confluence and MS Project
- Risk management and status reporting
- Stakeholder management up to executive level

Nice to have
- PMP or Certified Scrum Master
- Software delivery background
- Vendor management
- Change management
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

# ----------------------------------------------------- healthcare & education
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


def main():
    OUT.mkdir(exist_ok=True)
    for key, text in P.items():
        (OUT / f"{key}.txt").write_text(text, encoding="utf-8")
    print(f"wrote {len(P)} presets to {OUT}")


if __name__ == "__main__":
    main()
