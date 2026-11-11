BEGIN TRANSACTION;
CREATE TABLE activities (
  id INTEGER PRIMARY KEY,
  experience_id INTEGER NOT NULL REFERENCES experiences(id),
  label TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  active INTEGER NOT NULL DEFAULT 1
, master_id INTEGER REFERENCES descriptions(id));
INSERT INTO "activities" VALUES(1,1,'Tarifpublic.fr consulting',1,1,1);
INSERT INTO "activities" VALUES(2,1,'AI agent workflows',2,1,2);
INSERT INTO "activities" VALUES(3,1,'LingoWP plugin support',3,0,NULL);
INSERT INTO "activities" VALUES(4,2,'Hypeo product (description)',1,1,3);
INSERT INTO "activities" VALUES(5,2,'AI agent experience',2,1,4);
INSERT INTO "activities" VALUES(6,2,'Front-end with the tech lead',3,1,5);
INSERT INTO "activities" VALUES(7,2,'Influencer data extraction',4,1,6);
INSERT INTO "activities" VALUES(8,2,'Ownership during the leadership transition',5,1,7);
INSERT INTO "activities" VALUES(9,2,'Documentation of modules and architecture',6,1,8);
INSERT INTO "activities" VALUES(10,2,'Creator data-metrics solution',7,1,9);
INSERT INTO "activities" VALUES(11,2,'Moderation platform',8,0,NULL);
INSERT INTO "activities" VALUES(12,3,'Standardized delivery process (description)',1,1,10);
INSERT INTO "activities" VALUES(13,3,'Reusable prototyping approach',2,1,11);
INSERT INTO "activities" VALUES(14,3,'Sprint KPIs in Odoo',3,1,12);
INSERT INTO "activities" VALUES(15,3,'02Book to production',4,1,13);
INSERT INTO "activities" VALUES(16,3,'Growth under mentorship',5,1,14);
INSERT INTO "activities" VALUES(17,4,'Inflauditor and landing pages (description)',1,1,15);
INSERT INTO "activities" VALUES(18,4,'UI flows and prototypes',2,1,16);
INSERT INTO "activities" VALUES(19,4,'Data insights',3,1,17);
INSERT INTO "activities" VALUES(20,5,'CTF platform (description)',1,1,18);
INSERT INTO "activities" VALUES(21,5,'Go API service',2,1,19);
INSERT INTO "activities" VALUES(22,5,'Warzone dashboard',3,1,20);
INSERT INTO "activities" VALUES(23,5,'Coaching and mentoring',4,0,NULL);
INSERT INTO "activities" VALUES(24,6,'Subscription website (description)',1,1,21);
INSERT INTO "activities" VALUES(25,7,'Solar onboarding experiences (description)',1,0,NULL);
INSERT INTO "activities" VALUES(26,7,'Website delivery automation',1,1,22);
INSERT INTO "activities" VALUES(27,7,'Lead-capture websites',2,1,23);
INSERT INTO "activities" VALUES(28,4,'Landing pages (former Digital Consulting entry)',4,0,NULL);
CREATE TABLE certifications (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  issuer TEXT NOT NULL,
  link TEXT NOT NULL,
  date TEXT
);
INSERT INTO "certifications" VALUES(1,'Building with the Claude API','Anthropic','https://www.masayagh.com/badge/claude-api',NULL);
INSERT INTO "certifications" VALUES(2,'Model Context Protocol: Advanced Topics','Anthropic','https://www.masayagh.com/badge/mcp-advanced-topics',NULL);
INSERT INTO "certifications" VALUES(3,'Fundamentals of Agents','Hugging Face','https://www.masayagh.com/badge/fundamentals-of-agents',NULL);
CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL CHECK (kind IN ('employer', 'prospect')),
  international INTEGER NOT NULL DEFAULT 0,
  country TEXT
);
INSERT INTO "companies" VALUES(1,'Technical Consultant','employer',0,NULL);
INSERT INTO "companies" VALUES(2,'Phoenix AI USA Inc.','employer',0,NULL);
INSERT INTO "companies" VALUES(3,'Cogy Tech','employer',0,NULL);
INSERT INTO "companies" VALUES(4,'Rich Media','employer',0,NULL);
INSERT INTO "companies" VALUES(5,'Cyber Cohesion','employer',0,NULL);
INSERT INTO "companies" VALUES(6,'Sodiadd','employer',0,NULL);
INSERT INTO "companies" VALUES(7,'Jonas Agency','employer',0,NULL);
INSERT INTO "companies" VALUES(8,'Happy Water NFT','employer',0,NULL);
INSERT INTO "companies" VALUES(9,'Lavish Trading','employer',0,NULL);
INSERT INTO "companies" VALUES(10,'MySchool','employer',0,NULL);
INSERT INTO "companies" VALUES(11,'Freelance','employer',0,NULL);
INSERT INTO "companies" VALUES(12,'theodo','prospect',0,NULL);
INSERT INTO "companies" VALUES(13,'Theodo','prospect',0,NULL);
INSERT INTO "companies" VALUES(14,'Oracle','prospect',0,NULL);
INSERT INTO "companies" VALUES(15,'Y Strategie','prospect',0,NULL);
INSERT INTO "companies" VALUES(16,'CGI','prospect',0,NULL);
CREATE TABLE contact (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  phone_link TEXT NOT NULL,
  location_en TEXT NOT NULL,
  location_fr TEXT,
  website TEXT NOT NULL,
  website_link TEXT NOT NULL,
  github TEXT,
  linkedin TEXT
);
INSERT INTO "contact" VALUES(1,'Mohamed Amine Sayagh','mohamedamine@masayagh.com','(+212) 616-13 71 24','tel:+212616137124','Casablanca, Morocco','Casablanca, Maroc','masayagh.com/hire','https://www.masayagh.com/hire','https://github.com/aminesayagh','https://linkedin.com/in/mohamedamine-sayagh');
CREATE TABLE cover_paragraph_experiences (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id),
  experience_id INTEGER NOT NULL REFERENCES experiences(id),
  PRIMARY KEY (paragraph_id, experience_id)
);
INSERT INTO "cover_paragraph_experiences" VALUES(2,2);
INSERT INTO "cover_paragraph_experiences" VALUES(3,5);
CREATE TABLE cover_paragraph_skills (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id),
  skill_id INTEGER NOT NULL REFERENCES skills(id),
  PRIMARY KEY (paragraph_id, skill_id)
);
INSERT INTO "cover_paragraph_skills" VALUES(1,79);
INSERT INTO "cover_paragraph_skills" VALUES(2,73);
INSERT INTO "cover_paragraph_skills" VALUES(2,74);
INSERT INTO "cover_paragraph_skills" VALUES(3,79);
CREATE TABLE cover_paragraphs (
  id INTEGER PRIMARY KEY,
  part TEXT NOT NULL CHECK (part IN ('opening', 'example', 'support', 'close')),
  text_en TEXT NOT NULL UNIQUE,
  text_fr TEXT,
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  first_offer_id INTEGER REFERENCES offers(id),
  created_at TEXT NOT NULL DEFAULT (date('now'))
, default_order INTEGER);
INSERT INTO "cover_paragraphs" VALUES(1,'opening','I am applying for the {job_title} role at {company}. My work has focused on building software that helps people carry out complex tasks, from campaign setup to security competitions.',NULL,'approved',NULL,'2026-11-11',1);
INSERT INTO "cover_paragraphs" VALUES(2,'example','At Hypeo, I integrated an AI agent experience that turns client conversations into configured marketing campaigns using an internal influencer database. Working closely with a senior technical lead, I refined the front-end experience as the backend integration and business requirements evolved.',NULL,'approved',NULL,'2026-11-11',2);
INSERT INTO "cover_paragraphs" VALUES(3,'support','At Cyber Cohesion, I led web development for a security competition platform used at events including OWASP AppSec Days and BSides Singapore. I also developed its Warzone dashboard, which tracks team progress and scores.',NULL,'approved',NULL,'2026-11-11',3);
INSERT INTO "cover_paragraphs" VALUES(4,'close','I would welcome the opportunity to discuss how my experience could support the work at {company}. Thank you for your consideration.',NULL,'approved',NULL,'2026-11-11',4);
CREATE TABLE description_skills (
  description_id INTEGER NOT NULL REFERENCES descriptions(id),
  skill_id INTEGER NOT NULL REFERENCES skills(id),
  PRIMARY KEY (description_id, skill_id)
);
INSERT INTO "description_skills" VALUES(2,3);
INSERT INTO "description_skills" VALUES(2,73);
INSERT INTO "description_skills" VALUES(6,74);
INSERT INTO "description_skills" VALUES(3,65);
INSERT INTO "description_skills" VALUES(3,69);
INSERT INTO "description_skills" VALUES(4,73);
INSERT INTO "description_skills" VALUES(4,74);
INSERT INTO "description_skills" VALUES(13,73);
INSERT INTO "description_skills" VALUES(11,42);
INSERT INTO "description_skills" VALUES(11,70);
INSERT INTO "description_skills" VALUES(12,38);
INSERT INTO "description_skills" VALUES(16,70);
INSERT INTO "description_skills" VALUES(19,67);
INSERT INTO "description_skills" VALUES(18,79);
INSERT INTO "description_skills" VALUES(24,62);
INSERT INTO "description_skills" VALUES(29,3);
INSERT INTO "description_skills" VALUES(29,73);
INSERT INTO "description_skills" VALUES(30,65);
INSERT INTO "description_skills" VALUES(30,69);
INSERT INTO "description_skills" VALUES(31,72);
INSERT INTO "description_skills" VALUES(31,73);
INSERT INTO "description_skills" VALUES(31,74);
INSERT INTO "description_skills" VALUES(32,13);
INSERT INTO "description_skills" VALUES(32,67);
INSERT INTO "description_skills" VALUES(34,79);
INSERT INTO "description_skills" VALUES(35,11);
INSERT INTO "description_skills" VALUES(35,34);
INSERT INTO "description_skills" VALUES(35,54);
INSERT INTO "description_skills" VALUES(35,56);
INSERT INTO "description_skills" VALUES(36,60);
INSERT INTO "description_skills" VALUES(36,67);
INSERT INTO "description_skills" VALUES(37,57);
INSERT INTO "description_skills" VALUES(37,70);
INSERT INTO "description_skills" VALUES(38,67);
INSERT INTO "description_skills" VALUES(40,11);
INSERT INTO "description_skills" VALUES(40,23);
INSERT INTO "description_skills" VALUES(40,26);
INSERT INTO "description_skills" VALUES(41,73);
INSERT INTO "description_skills" VALUES(41,74);
INSERT INTO "description_skills" VALUES(45,42);
INSERT INTO "description_skills" VALUES(45,70);
INSERT INTO "description_skills" VALUES(46,38);
INSERT INTO "description_skills" VALUES(47,73);
INSERT INTO "description_skills" VALUES(47,74);
INSERT INTO "description_skills" VALUES(48,9);
INSERT INTO "description_skills" VALUES(49,6);
INSERT INTO "description_skills" VALUES(51,73);
CREATE TABLE descriptions (
  id INTEGER PRIMARY KEY,
  experience_id INTEGER NOT NULL REFERENCES experiences(id),
  kind TEXT NOT NULL CHECK (kind IN ('description', 'bullet')),
  text_en TEXT NOT NULL,
  text_fr TEXT,
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  first_offer_id INTEGER REFERENCES offers(id),
  created_at TEXT NOT NULL DEFAULT (date('now')), activity_id INTEGER REFERENCES activities(id),
  UNIQUE (experience_id, text_en)
);
INSERT INTO "descriptions" VALUES(1,1,'bullet','Tarifpublic.fr, provide technical consulting for a French state-supported marketplace for public procurement, supporting standardized product pricing.','Tarifpublic.fr : conseil technique pour une marketplace de la commande publique soutenue par l''État français, pour une tarification standardisée des produits.','approved',NULL,'2026-11-11',1);
INSERT INTO "descriptions" VALUES(2,1,'bullet','Develop AI agent workflows to automate business decisions for international agency engagements.','Workflows d''agents IA pour automatiser les décisions métier des missions d''agences internationales.','approved',NULL,'2026-11-11',2);
INSERT INTO "descriptions" VALUES(3,2,'description','Developed product features for Hypeo, a MENA creator-marketing SaaS platform connecting influencers and media creators with businesses launching online content campaigns.','Fonctionnalités produit pour Hypeo, plateforme SaaS de marketing d''influence (MENA) reliant influenceurs et créateurs aux entreprises qui lancent des campagnes de contenu en ligne.','approved',NULL,'2026-11-11',4);
INSERT INTO "descriptions" VALUES(4,2,'bullet','Integrated an AI agent experience that transforms open-ended client conversations into configured marketing campaigns, connected to the internal influencer database.','Intégration d''une expérience d''agent IA qui transforme des conversations clients ouvertes en campagnes marketing configurées, reliée à la base interne d''influenceurs.','approved',NULL,'2026-11-11',5);
INSERT INTO "descriptions" VALUES(5,2,'bullet','Built and refined the front-end experience in close collaboration with a senior technical lead, continuously adapting workflows to backend integration and evolving business requirements.','Conception et amélioration du front-end avec un lead technique senior, en adaptant les workflows à l''intégration back-end et à l''évolution des besoins métier.','approved',NULL,'2026-11-11',6);
INSERT INTO "descriptions" VALUES(6,2,'bullet','Automated the manipulation and extraction of influencer data from web-scraping outputs and database pipelines used across the platform.','Automatisation de l''extraction et du traitement des données d''influenceurs issues du web scraping et des pipelines de données de la plateforme.','approved',NULL,'2026-11-11',7);
INSERT INTO "descriptions" VALUES(7,2,'bullet','Took ownership of maintenance, deployment support, access/IP handover, and bug-fix coordination during a technical leadership transition.','Prise en charge de la maintenance, du support aux déploiements, de la passation des accès et de la PI, et de la coordination des correctifs lors d''une transition de direction technique.','approved',NULL,'2026-11-11',8);
INSERT INTO "descriptions" VALUES(8,2,'bullet','Documented core business modules, missing implementation areas, and architectural solutions to support future development planning.','Documentation des modules métier clés, des zones non implémentées et des solutions d''architecture pour la planification des développements futurs.','approved',NULL,'2026-11-11',9);
INSERT INTO "descriptions" VALUES(9,2,'bullet','Developed an external data-metrics solution for creator audience and professional collaboration insights, later accepted and integrated into the company workflow.','Solution externe de métriques sur l''audience des créateurs et leurs collaborations, ensuite adoptée et intégrée aux workflows de l''entreprise.','approved',NULL,'2026-11-11',10);
INSERT INTO "descriptions" VALUES(10,3,'description','Co-developed and rolled out a standardized software delivery process, aligning team workflows and contributing to lower shipping costs.','Co-conception et déploiement d''un processus standardisé de livraison logicielle, alignant les workflows de l''équipe et réduisant les coûts de livraison.','approved',NULL,'2026-11-11',12);
INSERT INTO "descriptions" VALUES(11,3,'bullet','Established a reusable prototyping approach to validate business requirements across multiple use cases before development.','Démarche de prototypage réutilisable pour valider les besoins métier sur plusieurs cas d''usage avant le développement.','approved',NULL,'2026-11-11',13);
INSERT INTO "descriptions" VALUES(12,3,'bullet','Tracked sprint KPIs in Odoo and surfaced bottlenecks to improve planning accuracy and throughput.','Suivi des KPI de sprint dans Odoo et identification des blocages pour fiabiliser la planification et augmenter le débit.','approved',NULL,'2026-11-11',14);
INSERT INTO "descriptions" VALUES(13,3,'bullet','Brought 02Book to production, an AI-powered writing assistant for B2B writers, used by clients such as Orange and Le Matin.','Mise en production de 02Book, assistant de rédaction IA pour rédacteurs B2B, utilisé par des clients comme Orange et Le Matin.','approved',NULL,'2026-11-11',15);
INSERT INTO "descriptions" VALUES(14,3,'bullet','Strengthened software design skills under continuous mentorship, working on client requirements and delivery constraints.','Montée en compétences en conception logicielle sous mentorat continu, sur des besoins clients et des contraintes de livraison.','approved',NULL,'2026-11-11',16);
INSERT INTO "descriptions" VALUES(15,4,'description','Designed and integrated product features for Inflauditor, a business decision-making dashboard that helps brands analyze large-scale creator data for campaign planning. Delivered high-conversion lead-capture landing pages for Miratti (Morocco), French Dandy (Dubai), and Horde Studio (USA), supporting growth campaigns showcased at regional events (e.g., Forbes Middle East).','Conception et intégration de fonctionnalités pour Inflauditor, tableau de bord d''aide à la décision qui permet aux marques d''analyser des données de créateurs à grande échelle. Landing pages de génération de leads à fort taux de conversion pour Miratti (Maroc), French Dandy (Dubaï) et Horde Studio (États-Unis), pour des campagnes présentées lors d''événements régionaux (ex. Forbes Middle East).','approved',NULL,'2026-11-11',17);
INSERT INTO "descriptions" VALUES(16,4,'bullet','Designed UI flows and prototypes for Inflauditor to validate product direction and accelerate development decisions.','Parcours UI et prototypes pour Inflauditor afin de valider l''orientation produit et d''accélérer les décisions de développement.','approved',NULL,'2026-11-11',18);
INSERT INTO "descriptions" VALUES(17,4,'bullet','Integrated data insights such as creator scoring, language detection, and sentiment indicators to support campaign planning.','Intégration d''indicateurs (scoring des créateurs, détection de langue, analyse de sentiment) pour la planification des campagnes.','approved',NULL,'2026-11-11',19);
INSERT INTO "descriptions" VALUES(18,5,'description','Led web development of a CTF platform for security competitions, used in global events such as OWASP AppSec Days, BSides Singapore, and ISACA.','Direction du développement web d''une plateforme CTF de compétitions de sécurité, utilisée lors d''événements comme OWASP AppSec Days, BSides Singapore et ISACA.','approved',NULL,'2026-11-11',20);
INSERT INTO "descriptions" VALUES(19,5,'bullet','Implemented a Go API service to orchestrate isolated application deployments, providing a secure training environment for participants.','Service API en Go orchestrant des déploiements d''applications isolées, pour un environnement d''entraînement sécurisé.','approved',NULL,'2026-11-11',21);
INSERT INTO "descriptions" VALUES(20,5,'bullet','Developed the web experience of Warzone, a dashboard to track team progress, scoring and overall competition gamification.','Expérience web de Warzone, tableau de bord de suivi de la progression des équipes, des scores et de la gamification.','approved',NULL,'2026-11-11',22);
INSERT INTO "descriptions" VALUES(21,6,'description','Developed a responsive subscription website for individual real estate investment plans.','Développement d''un site d''abonnement responsive pour des plans d''investissement immobilier individuels.','approved',NULL,'2026-11-11',24);
INSERT INTO "descriptions" VALUES(22,7,'bullet','Automated the delivery process for new websites by reusing proven experience patterns, helping shorten release cycles.','Automatisation de la livraison de nouveaux sites par la réutilisation de modèles éprouvés, réduisant les cycles de mise en production.','approved',NULL,'2026-11-11',26);
INSERT INTO "descriptions" VALUES(23,7,'bullet','Produced lead-capture websites that delivered strong conversion performance for client campaigns.','Sites de génération de leads à forte conversion pour les campagnes clients.','approved',NULL,'2026-11-11',27);
INSERT INTO "descriptions" VALUES(24,1,'bullet','LingoWP, maintain and support a multilingual WordPress plugin deployed across four digital agencies.',NULL,'approved',1,'2026-11-06',3);
INSERT INTO "descriptions" VALUES(25,4,'description','Designed and integrated product features for Inflauditor, a business decision-making dashboard that helps brands analyze large-scale creator data for campaign planning.',NULL,'approved',1,'2026-11-06',17);
INSERT INTO "descriptions" VALUES(26,4,'description','Delivered high-conversion lead-capture landing pages for Miratti (Morocco), French Dandy (Dubai), and Horde Studio (USA), supporting growth campaigns showcased at regional events (e.g., Forbes Middle East).',NULL,'approved',1,'2026-11-06',28);
INSERT INTO "descriptions" VALUES(27,7,'description','Delivered client onboarding web experiences for solar energy products, serving as the first digital touchpoint between customers and suppliers.',NULL,'approved',1,'2026-11-06',25);
INSERT INTO "descriptions" VALUES(28,1,'bullet','Tarifpublic.fr, provide full-stack technical consulting for a French state-supported marketplace for public procurement, supporting standardized product pricing.',NULL,'approved',4,'2026-11-09',1);
INSERT INTO "descriptions" VALUES(29,1,'bullet','Develop enterprise software with AI agent workflows that automate business decisions for international agencies.',NULL,'approved',4,'2026-11-09',2);
INSERT INTO "descriptions" VALUES(30,2,'description','Developed full-stack product features for Hypeo, a MENA creator-marketing SaaS platform connecting influencers and media creators with businesses launching online content campaigns.',NULL,'approved',4,'2026-11-09',4);
INSERT INTO "descriptions" VALUES(31,2,'bullet','Integrated an AI agent experience built on agentic systems, turning open-ended client conversations into configured marketing campaigns connected to the internal influencer database.',NULL,'approved',4,'2026-11-09',5);
INSERT INTO "descriptions" VALUES(32,2,'bullet','Built a data integration with external APIs for creator audience and professional collaboration metrics, later accepted and integrated into the company workflow.',NULL,'approved',4,'2026-11-09',10);
INSERT INTO "descriptions" VALUES(33,3,'description','Co-developed engineering standards for code quality and shipping, delivering standardized software to enterprise clients at lower cost.',NULL,'approved',4,'2026-11-09',12);
INSERT INTO "descriptions" VALUES(34,5,'description','Led web development of a CTF platform for security competitions, used in global events such as OWASP AppSec Days, BSides Singapore, and ISACA. Shared in managing teams and supported the hiring of new engineers.',NULL,'approved',4,'2026-11-09',20);
INSERT INTO "descriptions" VALUES(35,2,'bullet','Built and refined the front-end experience in Next.js, TypeScript and Tailwind CSS, creating reusable component libraries on Radix UI, in close collaboration with a senior technical lead.',NULL,'approved',5,'2026-11-09',6);
INSERT INTO "descriptions" VALUES(36,2,'bullet','Delivered a moderation platform in Vue 3 that let the team review and onboard creator profiles from one place, connected to Hypeo''s account API endpoints.',NULL,'approved',5,'2026-11-09',11);
INSERT INTO "descriptions" VALUES(37,4,'bullet','Owned UI design, UX flows and prototypes for Inflauditor to validate product direction and accelerate development decisions.',NULL,'approved',5,'2026-11-09',18);
INSERT INTO "descriptions" VALUES(38,5,'bullet','Implemented Go API endpoints to orchestrate isolated application deployments, providing a secure training environment for participants.',NULL,'approved',5,'2026-11-09',21);
INSERT INTO "descriptions" VALUES(39,5,'bullet','Provided coaching and mentoring to developers on the platform''s web experience.',NULL,'approved',5,'2026-11-09',23);
INSERT INTO "descriptions" VALUES(40,6,'description','Developed a responsive, accessible subscription website in HTML, CSS and JavaScript for individual real estate investment plans.',NULL,'approved',5,'2026-11-09',24);
INSERT INTO "descriptions" VALUES(41,2,'bullet','Integrated a generative AI agent experience that transforms open-ended client conversations into configured marketing campaigns, connected to the internal influencer database.',NULL,'approved',6,'2026-11-10',5);
INSERT INTO "descriptions" VALUES(42,2,'bullet','Built and refined the front-end experience in close collaboration with a senior technical lead, continuously adapting workflows to backend integration and evolving business requirements from stakeholders.',NULL,'approved',6,'2026-11-10',6);
INSERT INTO "descriptions" VALUES(43,2,'bullet','Took ownership of production systems maintenance, deployment support on cloud services, access/IP handover, incident response and bug-fix coordination during a technical leadership transition.',NULL,'approved',6,'2026-11-10',8);
INSERT INTO "descriptions" VALUES(44,3,'description','Co-developed engineering standards for code quality and shipping, delivering standardized software to enterprise customers at lower cost.',NULL,'approved',6,'2026-11-10',12);
INSERT INTO "descriptions" VALUES(45,3,'bullet','Established a reusable prototyping approach to validate business requirements and set technical priorities before development.',NULL,'approved',6,'2026-11-10',13);
INSERT INTO "descriptions" VALUES(46,3,'bullet','Tracked agile sprint KPIs in Odoo and surfaced bottlenecks to improve planning accuracy and throughput.',NULL,'approved',6,'2026-11-10',14);
INSERT INTO "descriptions" VALUES(47,2,'bullet','Integrated an AI agent experience built on Large Language Models that transforms open-ended client conversations into configured marketing campaigns, connected to the internal influencer database.',NULL,'approved',7,'2026-11-10',5);
INSERT INTO "descriptions" VALUES(48,2,'bullet','Built and refined the front-end experience in close collaboration and code review with a senior technical lead, continuously adapting workflows to backend integration and evolving business requirements.',NULL,'approved',7,'2026-11-10',6);
INSERT INTO "descriptions" VALUES(49,2,'bullet','Took ownership of production-grade software maintenance, CI/CD deployment support on cloud services, access/IP handover, debugging and bug-fix coordination during a technical leadership transition.',NULL,'approved',7,'2026-11-10',8);
INSERT INTO "descriptions" VALUES(50,2,'bullet','Documented core business modules, missing implementation areas, and software architecture solutions to support future engineering planning.',NULL,'approved',7,'2026-11-10',9);
INSERT INTO "descriptions" VALUES(51,3,'bullet','Brought 02Book to production, an AI-enabled writing assistant for B2B writers, used by clients such as Orange and Le Matin.',NULL,'approved',7,'2026-11-10',15);
CREATE TABLE education (
  id INTEGER PRIMARY KEY,
  degree_en TEXT NOT NULL,
  degree_fr TEXT,
  institution_en TEXT NOT NULL,
  institution_fr TEXT,
  start_at TEXT NOT NULL,
  end_at TEXT NOT NULL
);
INSERT INTO "education" VALUES(1,'Master''s in Big Data & Cloud Computing','Master en Big Data & Cloud Computing','University of Hassan 2, Casablanca','Université Hassan II, Casablanca','2023','2025');
INSERT INTO "education" VALUES(2,'Bachelor''s in Computer Science','Licence en informatique','University of Hassan 2, Casablanca','Université Hassan II, Casablanca','2020','2023');
CREATE TABLE experiences (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  role TEXT NOT NULL,
  detail TEXT,
  location TEXT,
  type TEXT NOT NULL CHECK (type IN ('job', 'freelance')),
  start_at TEXT NOT NULL,
  end_at TEXT,
  sort_order INTEGER NOT NULL
, company_fr TEXT, role_fr TEXT, detail_fr TEXT);
INSERT INTO "experiences" VALUES(1,1,'Software Developer','France','France','job','2026-09',NULL,0,'Consultant technique','Développeur logiciel',NULL);
INSERT INTO "experiences" VALUES(2,2,'Software Developer','- Hypeo, MENA',NULL,'job','2025-07','2026-09',1,NULL,'Développeur logiciel',NULL);
INSERT INTO "experiences" VALUES(3,3,'Software Developer','Morocco','Morocco','job','2025-02','2025-06',2,NULL,'Développeur logiciel','Maroc');
INSERT INTO "experiences" VALUES(4,4,'Software Developer','Morocco','Morocco','job','2024-08','2025-01',3,NULL,'Développeur logiciel','Maroc');
INSERT INTO "experiences" VALUES(5,5,'Software Developer','Singapore','Singapore','job','2023-08','2024-07',4,NULL,'Développeur logiciel','Singapour');
INSERT INTO "experiences" VALUES(6,6,'Software Developer','France','France','job','2023-05','2023-07',5,NULL,'Développeur logiciel',NULL);
INSERT INTO "experiences" VALUES(7,7,'Full Stack Developer','London','London','job','2022-10','2023-04',6,NULL,'Développeur Full Stack','Londres');
INSERT INTO "experiences" VALUES(8,8,'Software Developer','France','France','job','2022-07','2022-09',7,NULL,'Développeur logiciel',NULL);
INSERT INTO "experiences" VALUES(9,9,'Software Developer','London','London','job','2021-08','2022-06',8,NULL,'Développeur logiciel','Londres');
INSERT INTO "experiences" VALUES(10,10,'Software Developer','Morocco','Morocco','job','2021-01','2021-06',9,NULL,'Développeur logiciel','Maroc');
INSERT INTO "experiences" VALUES(11,11,'Web Designer','Morocco','Morocco','freelance','2016','2020',10,NULL,'Web designer','Maroc');
CREATE TABLE languages (
  id INTEGER PRIMARY KEY,
  sort_order INTEGER NOT NULL,
  name_en TEXT NOT NULL,
  name_fr TEXT,
  level_en TEXT NOT NULL,
  level_fr TEXT
);
INSERT INTO "languages" VALUES(1,1,'Arabic','Arabe','Native','Langue maternelle');
INSERT INTO "languages" VALUES(2,2,'French','Français','Professional','Professionnel');
INSERT INTO "languages" VALUES(3,3,'English','Anglais','Professional','Professionnel');
CREATE TABLE offer_results (
  offer_id INTEGER NOT NULL REFERENCES offers(id),
  requirement_id INTEGER NOT NULL REFERENCES requirements(id),
  term TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('met', 'partial', 'missing')),
  found_in TEXT,
  description_id INTEGER REFERENCES descriptions(id),
  snapshot_at TEXT NOT NULL
);
INSERT INTO "offer_results" VALUES(8,126,'Casablanca','met','header',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,127,'informatique','met','education',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,129,'Java','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,130,'Spring Boot','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,132,'AI Building','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,133,'IA agentique','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,134,'Back-End','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,135,'microservices','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,136,'event-driven','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,137,'bases de données','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,138,'Git','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,139,'CI/CD','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,140,'Sonar','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,141,'tests','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,142,'conception technique','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,143,'leadership','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,144,'problématiques complexes','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,145,'collaboration transverse','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,146,'orientation résultats','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,147,'intelligence artificielle','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,148,'architectures distribuées','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,149,'intelligence artificielle','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,150,'IA agentique','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,151,'Java','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,152,'Spring Boot','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,153,'microservices','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,154,'event-driven','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,155,'sources de données','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,156,'bases de données','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,157,'choix d''architecture','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,158,'performance','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,159,'sécurité','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,160,'revues de code','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,161,'tests techniques','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,162,'CI/CD','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(8,163,'équipes techniques','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,164,'Casablanca','met','header',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,165,'AI Software Engineer','met','header',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,166,'production-grade software','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,167,'APIs','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,167,'SDKs','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,168,'codebases','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,169,'Large Language Model','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,170,'testing','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,170,'performance','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,171,'technical designs','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,172,'engineering execution','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,173,'engineering standards','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,174,'Computer Science','met','education',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,174,'Software Engineering','partial','summary',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,175,'software engineering','partial','summary',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,176,'backend','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,177,'Java','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,177,'Python','met','projects',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,177,'C++','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,178,'data structures','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,178,'algorithms','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,179,'system design','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,179,'software architecture','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,180,'APIs','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,180,'SDKs','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,180,'libraries','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,181,'codebases','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,182,'AI systems','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,182,'Large Language Models','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,182,'AI application development','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,183,'CI/CD','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,184,'testing','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,184,'debugging','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,184,'performance analysis','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,185,'technical leadership','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,186,'code review','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,187,'design review','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,188,'mentoring','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,189,'engineering planning','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,190,'problem-solving','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,191,'communication','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,192,'AI-enabled','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,193,'distributed systems','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,193,'cloud services','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,194,'SDKs','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,194,'APIs','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,195,'RAG','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,195,'LLM orchestration','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,195,'agentic workflows','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,196,'observability','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,196,'AI governance','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(7,197,'technical lead','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,198,'full-stack','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,199,'front-end','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,200,'APIs','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,201,'data integration','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,202,'cloud','met','education',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,203,'hiring','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,203,'coaching','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,204,'managing teams','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,204,'matrixed','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,205,'enterprise software','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,205,'developer platforms','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,205,'frameworks','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,206,'engineering standards','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,207,'communication','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,208,'computer science','met','education',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,209,'AI-enabled products','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,209,'agentic systems','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,209,'AI-assisted developer tools','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,210,'Large language models','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,210,'agent orchestration','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,211,'SDKs','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,211,'developer tools','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,212,'distributed','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,212,'multicultural','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,213,'site reliability engineering','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,213,'incident management','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,214,'Master’s degree','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,215,'testing','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,215,'observability','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,216,'distributed systems','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(4,217,'Morocco','met','header',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,218,'Casablanca','met','header',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,219,'Computer Science','met','education',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,221,'people-management','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,222,'managing managers','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,223,'complex software','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,224,'stakeholders','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,225,'cloud services','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,226,'agile','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,227,'security','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,228,'operational reliability','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,229,'production systems','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,230,'enterprise customers','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,231,'incident response','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,232,'technical priorities','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,233,'communication','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,234,'stakeholder-management','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,235,'organizational leadership','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,236,'English','met','languages',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,237,'French','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,237,'Arabic','met','languages',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,238,'coach','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,239,'roadmaps','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,240,'architecture reviews','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,241,'code quality','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,241,'testing','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,242,'incident management','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,243,'hiring','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,244,'performance management','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,245,'cloud','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,245,'automation','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,245,'AI','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,246,'budgets','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,247,'enterprise software','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,248,'developer platforms','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,248,'data platforms','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,249,'machine learning','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,249,'generative AI','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,250,'distributed engineering','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,251,'EMEA','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,252,'Oracle products','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,253,'workforce planning','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(6,253,'budget management','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,255,'Vue 3','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,256,'composition API','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,257,'Tailwind CSS','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,258,'HTML','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,259,'accessible','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,260,'component libraries','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,260,'design systems','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,261,'Laravel','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,261,'Blade','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,262,'API','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,263,'jQuery','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,264,'Coaching','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,264,'mentoring','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,265,'JavaScript','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,266,'ES6','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,267,'TypeScript','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,268,'HTML5','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,269,'CSS','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,269,'SCSS','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,269,'SASS','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,270,'Git','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,271,'CI/CD','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,272,'performance optimisation','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,273,'Laravel Mix','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,273,'Vite','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,273,'Sanctum','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,274,'Docker','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,274,'WAMP','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,274,'LAMP','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,275,'API endpoints','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,276,'Pinia','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,276,'state management','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,277,'VeeValidate','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,278,'Accessibility','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,278,'WCAG','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,279,'Maizzle','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,280,'AI/ML','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,281,'UI Design','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,282,'UX','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,283,'prototype','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,284,'Jest','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,284,'Vitest','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,284,'Cypress','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,285,'jQuery','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,285,'Vue 3','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,286,'component library','missing',NULL,NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,287,'accessibility','partial','skills',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,287,'performance','met','experience',NULL,'2026-11-11');
INSERT INTO "offer_results" VALUES(5,288,'Casablanca','met','header',NULL,'2026-11-11');
CREATE TABLE offers (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  title TEXT NOT NULL,
  link TEXT,
  folder TEXT NOT NULL UNIQUE,
  pdf_name TEXT NOT NULL,
  resume_url TEXT,
  cover_letter_url TEXT,
  published_at TEXT,
  language TEXT NOT NULL CHECK (language IN ('en', 'fr')),
  french_version INTEGER NOT NULL DEFAULT 0,
  location TEXT,
  location_match TEXT,
  posting TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft', 'ready', 'sent')),
  created_at TEXT NOT NULL,
  sent_at TEXT,
  previous_offer_id INTEGER REFERENCES offers(id)
, company_slug TEXT, template_sha TEXT, skipped_terms TEXT);
INSERT INTO "offers" VALUES(1,12,'Software Engineer',NULL,'jobs/theodo-software-engineer-fullstack-v1','Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','https://www.masayagh.com/resume/theodo/Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf',NULL,NULL,'fr',0,NULL,NULL,'L’histoire du groupe Theodo et son succès
Theodo accompagne depuis 2009 les entreprises innovantes dans la conception, le développement et le déploiement de produits digitaux ingénieux - tels que la plateforme TF1+, l''application LCL Pro ou l''application France Identité Numérique - en tirant parti du meilleur de la technologie et de l’approche Lean.
 
Theodo connait une croissance exceptionnelle depuis 15 ans : nos équipes rassemblent plus de 750 Theodoers, principalement des Software Engineers, passionnés de technologie et d’amélioration continue. En 2025, le groupe Theodo génère 100M€ de CA.

Ton équipe :
Tu rejoindras une communauté tech de plus de 120 Theodoers : software engineers, tech leads, engineering managers et architectes, avec lesquels tu pourras échanger, apprendre et progresser au quotidien.
 
Chez Theodo, les techs travaillent en équipes projet, constituées en fonction des besoins de chaque client. Tu feras partie d’une équipe de Theodoers à taille humaine (4 à 5 personnes), réunissant Software Engineers, Tech Lead et Product Manager. Ensemble, vous collaborerez étroitement avec le client, avec des échanges réguliers pour partager vos avancées, approfondir la compréhension de son problème et faire évoluer le produit au plus près des besoins de ses utilisateurs.
 
Tes futures missions :
En tant que Software Engineer Fullstack chez Theodo, ta mission sera de concevoir et développer des produits digitaux utiles, performants et durables pour répondre aux problématiques de nos clients et de leurs utilisateurs.
 
Tout au long de tes projets, tu seras accompagné pour monter en compétences et apprendre à écrire du code de qualité, à comprendre les enjeux produit et à intervenir sur l’ensemble du cycle de vie d’une application, de la conception au déploiement.
 
Ce que tu vas apprendre en tant que Software Engineer chez Theodo :
Comprendre le problème de ton client et y répondre avec un produit performant, maintenable et orienté valeur, en intervenant sur tout le cycle de production, de la conception au déploiement.
Produire du code de qualité dans les délais, en intégrant tests, refactoring et standards techniques de l’équipe, quelle que soit la technologie utilisée.
Mener des investigations techniques, débugger efficacement et corriger les défauts de manière pérenne, dans tout type d’environnement.
Analyser en profondeur des problèmes dans le code pour développer son esprit de résolution de problèmes
Travailler avec un LLM pour accélérer les développements
Les problématiques et les technos sont très différentes d’un projet à l’autre, voici quelques exemples :
iDealwine® : leader mondial des enchères de vins en ligne a engagé la migration de son site e-commerce monolithique vers une architecture composable pour gagner en évolutivité, en sécurité et en maîtrise technologique. Après 2 mois de cadrage, les équipes Theodo ont piloté une approche design-to-cost permettant de modulariser la plateforme et de migrer 20 ans d’historique en 14 mois, dans le respect du budget et du planning.
Sevetys : refonte complète d’une web app métier avec deux volets stratégiques : un outil de prise de rendez-vous pour les propriétaires d’animaux et un back-office dédié aux vétérinaires. Deux équipes produit ont piloté la reconstruction des plateformes de bout en bout, rejointes en fin de projet par une équipe data pour structurer et valoriser les données. Principal défi : une mise en production coordonnée à grande échelle, impliquant de nombreuses cliniques vétérinaires, sans interruption d’activité.
 
Parmi les technos les plus représentées sur nos projets, tu pourras être amené à travailler avec : Java (Spring Boot), Angular, Node (Nest), React (Next), Python… 
 
Tes perspectives d''évolution :
Notre ambition est de former les leaders de la tech de demain. Grâce au coaching et formations que l’on propose, tu pourras :
Devenir un expert en développement en étant formé aux meilleurs standards de qualité
Développer des compétences transverses : coaching, recrutement, commercial, management et marketing technique
Participer à des groupes d’expertises avec d’autres passionnés (Cybersécurité, Serverless, Performance, GreenIT…)
Construire ton parcours sur-mesure pour atteindre tes objectifs : tech lead, senior architecte, évangéliste (spécialiste d’un sujet), CTO ou fondateur d’une entité etc
 
Une méthodologie basée sur l’apprentissage continu :
Chez Theodo, nous avons construit notre approche tech autour d’une conviction forte : on développe d’abord les personnes, avant de développer les produits.
 
Notre Lean Tech® System met l’accent sur l’apprentissage continu : tu évolueras dans un environnement qui investit sur le long terme, où l’objectif est de te permettre de progresser chaque jour, tout en construisant des produits utiles et performants pour nos clients.
 
Profil recherché :
Nous recherchons avant tout des potentiels plus que des compétences déjà acquises. Si tu n’es pas encore un·e développeur·se chevronné·e, ce n’est pas un frein : ne te retiens pas pour postuler.
 
Tu es diplômé·e d’une top école d’ingénieur
Tu as entre 0 et 2 ans d''expérience
Tu aimes travailler en équipe et intéragir avec des profils et des métiers variés, en faisant preuve de pédagogie et d’esprit constructif (revues de code, pair programming)
Tu es orienté·e création de valeur : tu t’intéresses à l’activité du client et tu ne fais pas de la tech pour la tech
Tu es promoteur de l’IA, notamment sur les sujets de GenAI, et tu cherches à progresser en continu grâce à la veille technique
Tu fais preuve d’exigence sur la qualité du travail produit et sais questionner, voire interrompre, la chaîne de production lorsque nécessaire (#jidoka)
Tu aimes travailler de manière structurée et appliques naturellement des principes d’organisation et d’amélioration continue (inspirés du 5S)
Tu souhaites évoluer dans un environnement qui encourage au quotidien l’envie de progresser, l’esprit d’équipe et la prise d’initiative
 
Le processus de recrutement :
Un premier call de 30 minutes avec un recruteur
Un échange d’une heure avec le même recruteur
Un exercice de refactoring à effectuer chez toi, suivi d’un échange avec un tech lead pour revenir sur tes erreurs
Un exercice en direct de debuging
Un entretien dirigeant de 30 minutes pour revenir sur tes motivations à rejoindre Theodo et répondre à tes derniers questions
€40,000 - €50,000 a year
Pourquoi rejoindre Theodo ?
L’environnement:
💼 Rejoindre un groupe de 750 personnes avec de nombreuses possibilités d’évolutions cross-entités
🤝  Chaque Theodoer est accompagné par un coach interne. Son objectif : t’épauler dans ton quotidien et parler objectifs de carrière via des séances de coaching hebdomadaires.
🎯 Participation à des projets associatifs grâce à la Fondation Theodo (Ada Tech School, Code Phoenix, Article 1…)
🎉 Soirées mensuelles, keynotes et week-end d’entreprise annuel
 
Le package :
📈 Actionnariat salarié pour être associé à la réussite du groupe
💸 De l’épargne salariale avec un mécanisme d’intéressement en partenariat avec Epsor
🖥 Budget équipement (ordinateur, smartphone, écouteurs…)
🧒 Des avantages fournis par notre CSE (sport avec Gymlib,...)
🏖 5 semaines + 8 à 12 RTT/an
🩺 Mutuelle (SideCare) prise en charge à 50%
🍽 Carte ticket-restaurants Swile
🧒 Aides et places en crèche réservées
 
Prêt à nous rejoindre ?
','sent','2026-11-06','2026-11-11',NULL,'theodo',NULL,'{}');
INSERT INTO "offers" VALUES(2,13,'Software Engineer',NULL,'jobs/theodo-software-engineer-v1','Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','https://www.masayagh.com/resume/theodo/Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf',NULL,NULL,'fr',0,NULL,NULL,'L’histoire du groupe Theodo et son succès
Theodo accompagne depuis 2009 les entreprises innovantes dans la conception, le développement et le déploiement de produits digitaux ingénieux - tels que la plateforme TF1+, l''application LCL Pro ou l''application France Identité Numérique - en tirant parti du meilleur de la technologie et de l’approche Lean.
 
 
Theodo connait une croissance exceptionnelle depuis 15 ans : nos équipes rassemblent plus de 750 Theodoers, principalement des Software Engineers, passionnés de technologie et d’amélioration continue. En 2025, le groupe Theodo génère 100M€ de CA.
 
L’histoire de Theodo au Maroc commence en 2017, avec la création de Nimbleways, une entreprise tech fondée par un entrepreneur marocain ayant l''ambition de faire de "la world class tech made in Morocco". En 2019, Nimbleways rejoint le groupe Theodo et en adopte le nom quelques années plus tard.
Aujourd’hui, Theodo compte plus de 80 Theodoers à Casablanca. Nous partageons la même mission que nos homologues à Paris ou Londres : accompagner des scales-ups et de grandes entreprises au Maroc et à l''international dans la conception, le développement et la maintenance de produits digitaux ingénieux.

Chez Theodo Morocco , nous sommes constamment à la recherche de nouveaux talents pour rejoindre nos équipes. Si vous ne trouvez pas votre poste idéal parmi nos offres en ligne, ne laissez pas cela vous arrêter. Nous croyons fermement que chaque talent unique peut contribuer à notre succès !
 
#LI-DNI
#LI-DNI

Pourquoi rejoindre Theodo Morocco ?
Chez Theodo Morocco, l’amélioration continue est au cœur de notre culture. Dès votre arrivée, vous bénéficierez de :
 
- Un onboarding structuré et un coach dédié pour une montée en compétence rapide.
- Des rituels Lean (dojos, rétrospectives, kaizen) pour avancer efficacement.
- Un accès direct aux experts (CTO, architectes, tech leads) pour échanger et innover.
- Participez à des guildes d''expertises (Serverless, Sécurité, GreenIT, etc.).
- Une communauté tech active (tech talks, hackathons, meetups) pour partager et progresser.
- Des projets variés et stimulants : travaillez sur des applications mobiles innovantes, des plateformes e-commerce performantes, et bien plus encore.
- Un réseau international : collaborez avec plus de 450 développeur au sein du groupe Theodo répartis en France, au Maroc et au UK.
- Des perspectives de carrière : développez vos compétences techniques et transversales (coaching, marketing technique, recrutement) et accédez à des opportunités d’évolution vers des rôles de leadership.
 
Prêt à nous rejoindre ?
','sent','2026-11-08','2026-11-11',NULL,'theodo',NULL,'{}');
INSERT INTO "offers" VALUES(3,13,'Software Engineer',NULL,'jobs/theodo-software-engineer-v2','Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','https://www.masayagh.com/resume/theodo/v2/Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf',NULL,NULL,'fr',0,NULL,NULL,'L’histoire du groupe Theodo et son succès
Theodo accompagne depuis 2009 les entreprises innovantes dans la conception, le développement et le déploiement de produits digitaux ingénieux - tels que la plateforme TF1+, l''application LCL Pro ou l''application France Identité Numérique - en tirant parti du meilleur de la technologie et de l’approche Lean.
 
 
Theodo connait une croissance exceptionnelle depuis 15 ans : nos équipes rassemblent plus de 750 Theodoers, principalement des Software Engineers, passionnés de technologie et d’amélioration continue. En 2025, le groupe Theodo génère 100M€ de CA.
 
L’histoire de Theodo au Maroc commence en 2017, avec la création de Nimbleways, une entreprise tech fondée par un entrepreneur marocain ayant l''ambition de faire de "la world class tech made in Morocco". En 2019, Nimbleways rejoint le groupe Theodo et en adopte le nom quelques années plus tard.
Aujourd’hui, Theodo compte plus de 80 Theodoers à Casablanca. Nous partageons la même mission que nos homologues à Paris ou Londres : accompagner des scales-ups et de grandes entreprises au Maroc et à l''international dans la conception, le développement et la maintenance de produits digitaux ingénieux.

Depuis 7 ans, les bureaux marocains de Theodo veillent à la transformation d’idées de clients en solutions tech. Nous les accompagnons dans le design et le lancement de produits digitaux qui répondent à leurs problématiques business, en un temps record.
 
Pour faire réussir les projets de nos clients, nous recherchons des Tech Lead qui auront pour mission de:
- Accompagner le client dans la conception du meilleur produit qui répondra à ses besoins business
- Piloter une équipe de développement, en participant au code avec un focus sur la qualité
- Générer de la connaissance et la diffuser à Theodo:
- Tu partages tes apprentissages au sein de Theodo et à l’extérieur, grâce aux articles de blog et aux formations hebdomadaires
- Tu fais de la veille technique pour améliorer le craftsmanship au sein de Theodo.
 
Tes moyens pour réussir:
- La collaboration forte de nos équipes au Maroc avec tout le groupe Theodo: Plus de 450 crafters, une 10aine d''expertises et +200 projets réalisés
- Tu auras un coach expert tech dédié à ta réussite et progression.
 
Tes perspectives
Notre ambition est de former les leaders de la tech de demain.
Grâce au coaching et formations que l''on propose, tu pourras :
- Développer de l’expertise technique sur les sujets tech qui te passionnent
- Avoir l’opportunité de construire des compétences transverses : management, coaching, marketing technique, recrutement et commercial
- Participer à des guildes d’expertises (Serverless, Performance, Sécurité, GreenIt...) pour améliorer tes pratiques et celles de ton équipe.
 
Ce que nous recherchons:
- Tu es diplômé·e d''une école d''ingénieur ou équivalent
- Avoir un minimum de 5ans d’expérience dans le développement de logiciels, idéalement fullstack
- Tu as au moins 1 année d’expérience dans la gestion d’une équipe de développeurs
Pourquoi rejoindre Theodo Morocco ?
Chez Theodo Morocco, l’amélioration continue est au cœur de notre culture. Dès votre arrivée, vous bénéficierez de :
 
- Un onboarding structuré et un coach dédié pour une montée en compétence rapide.
- Des rituels Lean (dojos, rétrospectives, kaizen) pour avancer efficacement.
- Un accès direct aux experts (CTO, architectes, tech leads) pour échanger et innover.
- Participez à des guildes d''expertises (Serverless, Sécurité, GreenIT, etc.).
- Une communauté tech active (tech talks, hackathons, meetups) pour partager et progresser.
- Des projets variés et stimulants : travaillez sur des applications mobiles innovantes, des plateformes e-commerce performantes, et bien plus encore.
- Un réseau international : collaborez avec plus de 450 développeur au sein du groupe Theodo répartis en France, au Maroc et au UK.
- Des perspectives de carrière : développez vos compétences techniques et transversales (coaching, marketing technique, recrutement) et accédez à des opportunités d’évolution vers des rôles de leadership.
 
Prêt à nous rejoindre ?
','sent','2026-11-08','2026-11-11',NULL,'theodo','dfcf8ca573bf37c22de25c4f50f025b39c716ee3dc3b1083f35b37f4fea076c5','{}');
INSERT INTO "offers" VALUES(4,14,'Senior Manager, Platform Software Engineering',NULL,'jobs/oracle-senior-manager-platform-software-engineering-v1','Mohamed-Amine-Sayagh-Senior-Manager-Platform-Software-Engineering-Oracle.pdf','https://www.masayagh.com/resume/oracle/Mohamed-Amine-Sayagh-Senior-Manager-Platform-Software-Engineering-Oracle.pdf',NULL,NULL,'en',0,NULL,NULL,'Job Description
Leads one or more platform teams; defines tactical and key strategic elements for middleware evolution serving multiple consumers. Accountable for performance, cost control, and reliability outcomes; escalations for distributed debugging and upgrade safety. Drives significant cross-team improvements to observability, SLOs, and resilience patterns. Engages stakeholders inside and outside the group; socializes migration plans and adoption playbooks.
Responsibilities
We are looking for a Senior Manager of Software Development to build, lead and develop a multidisciplinary engineering team in Morocco.

Your team will work on strategic engineering capabilities spanning artificial intelligence, application infrastructure, UI frameworks and AI development tooling. Engineers will work in a matrixed model, partnering with domain leaders responsible for products and solutions including Nitro AI Development Framework, AI Fabric and AI Agent Studio.

This is a role for an engineering leader who enjoys building both high-performing teams and technology. You will combine people leadership with strong technical judgement, helping engineers turn rapidly evolving AI technologies into secure, reliable and usable platforms and services.

What you’ll do:

Build and lead the Morocco engineering team

Build, lead and develop a high-performing software engineering organisation in Morocco.

Recruit and retain engineers across AI, full-stack development, application infrastructure, developer tooling and UI frameworks.

Set clear goals and provide ongoing coaching, feedback, career development and performance management.

Develop technical leaders and create growth opportunities for engineers at different career stages.

Build an inclusive, collaborative and accountable engineering culture.

Provide technical and delivery leadership

Provide technical direction across AI-enabled applications, full-stack services, application infrastructure, UI frameworks and developer platforms.

Guide teams in designing and delivering scalable, secure and reliable software and services.

Establish strong engineering standards across architecture, APIs, testing, observability, reliability and software development.

Help teams solve complex technical issues across distributed systems and services.

Balance rapid experimentation with the engineering rigour required for enterprise-grade services.

Drive improvements in platform performance, resilience, operational readiness and engineering quality.

Work across teams and organisations

Lead engineers working in a matrixed model with functional and domain leaders.

Partner with domain leaders to align assignments, priorities, deliverables, staffing needs and performance expectations.

Build trusted relationships across engineering, industry teams and other partner organisations.

Represent the Morocco engineering organisation in planning, architecture, delivery and operational reviews.

Communicate technical decisions, priorities and risks clearly to engineering and business stakeholders.

Adapt as business priorities, customer needs and AI technologies evolve.

Required experience:

Strong full-stack software development expertise, including modern front-end technologies, service development, APIs, data integration and cloud-based application architectures.

Experience hiring, developing, coaching and retaining high-performing software engineers.

Demonstrated success managing teams in a matrixed organisation, with shared accountability across functional and delivery leaders.

Experience delivering enterprise software, cloud services, developer platforms, frameworks or shared engineering capabilities.

Experience establishing and improving engineering standards and practices.

Strong written and verbal communication skills, with the ability to explain complex technical and organisational topics clearly.

Bachelor’s degree in computer science, engineering or a related technical field, or equivalent practical experience.

Preferred experience:

Experience in one or more of the following would be valuable:

Building AI-enabled products, agentic systems, generative AI platforms or AI-assisted developer tools.

Large language models, agent orchestration, prompt and context management, model evaluation, AI guardrails, feedback systems or AI observability.

Building reusable SDKs, frameworks, APIs, developer tools or internal engineering platforms.

Managing geographically distributed or multicultural engineering teams.

Service management, site reliability engineering, incident management or operational readiness.

Master’s degree in computer science, engineering, business administration or a related discipline.

Career Level: M3

Qualifications
Career Level - M3

Required Skills
Application Platforms
Platform Development
Software Management
Software Platform Development
','sent','2026-11-09','2026-11-11',NULL,'oracle',NULL,'{}');
INSERT INTO "offers" VALUES(5,15,'Senior Front-End Developer','https://ystrategie.teamtailor.com/jobs/8670374-senior-front-end-developer','jobs/y-strategie-senior-front-end-developer-v1','Mohamed-Amine-Sayagh-Senior-Front-End-Developer-Y-Strategie.pdf','https://www.masayagh.com/resume/y-strategie/Mohamed-Amine-Sayagh-Senior-Front-End-Developer-Y-Strategie.pdf',NULL,NULL,'en',0,'Casablanca, Morocco','same city','Source: https://ystrategie.teamtailor.com/jobs/8670374-senior-front-end-developer
Location: Casablanca, Morocco

The Role
We''re looking for a Senior Front End Developer to join our IT Development team, reporting to the Digital Transformation Manager and CDO. You''ll be the front-end specialist in a team of 3 (2 mid-level devs, 1 principal dev), building and modernising the systems that power our business.
This is a hands-on role for a "Senior" developer, someone who''s solidified in their senior skillset and is ready to take ownership of our front-end architecture while supporting and coaching mid-level developers. You''ll lead by example, not by title.

What You''ll Be Doing
Day to day, you''ll:
· Build new features for our three core custom systems a sales quoting tool, customer portal, and digital onboarding platform
· Work alongside back-end developers on API endpoints, to support data being delivery to the front end.
· Migrate our legacy jQuery-based code to Vue 3 (a current modernisation project)
· Create and maintain reusable Vue 3 component libraries to bring alignment across our systems
· Build a robust front-end ecosystem that our backend team can efficiently integrate with. This would include
· Build a component library, with references and documenting components for the team to use.
· Optimizing current components and making them modular while making sure legacy logic is not lost.
· Making sure front end assets and component libraries are up to date.

In your first 6 months, you''ll:
· Establish our Vue 3 component architecture, introduce reusable, well documented components that eliminate duplication across systems
· Be the front-end authority become the go to expert that our 3 backend developers collaborate with on API design and integration
· Lead the FE for our system migration drive the technical approach and execution of moving from jQuery to Vue 3, setting the standard for future modernisation work

Coaching & Collaboration
· Support and mentor our two mid-level developers through code reviews, pair programming, and technical guidance
· Champion best practices in component architecture, performance, and accessibility
· Document front end patterns and standards to upskill the wider team

What We''re Looking For
· Essential Experience
· 5+ years of professional front end development experience
· 2+ years working with Vue 3 composition API in production applications
· Strong Tailwind CSS skills building responsive, maintainable UIs at scale
· Strong understanding of HTML markup Making sure the HTML is valid, confirms wc3 rules and is accessible for users.
· Proven experience creating reusable component libraries or design systems
· Laravel Blade templating experience you''ll need to navigate and enhance existing Blade views
· API development - comfortable writing Laravel endpoints or strong ability to collaborate with backend developers on API design
· jQuery experience you''ll be migrating it, so you need to understand what you''re replacing
· Coaching or mentoring experience supporting junior to mid-level developers

Technical Skills
· JavaScript/TypeScript (ES6+)
· HTML5 and modern CSS/SCSS/SASS
· Using Version control Git (how to merge, resolve merge conflicts and create and push branches)
· Git workflow and CI/CD basics
· Understanding of performance optimisation techniques

About You
· You enjoy building stuff right - creating scalable, reusable solutions that last
· You''re a collaborator, not a siloed coder our backend team needs your expertise
· You''re patient and supportive coaching mid-level devs energises you, rather than frustrates you
· You''re productive remotely self-motivated and communicative
· You balance pragmatism with quality you know when to perfect and when to ship

Desirable (Nice to Have)
· Experience with Laravel ecosystem (e.g., Laravel Mix, Vite, Sanctum)
· Docker/ WAMP/LAMP
· Able to write and maintain API endpoints to support front end functionality
· Pinia or other Vue state management
· VeeValidate
· Accessibility (WCAG) expertise
· Have used or have experience within Maizzle
· AI/ML application interfaces
· UI Design experience background
· UX Making sure the experience for the user is as slick as possible
· Able to rapidly prototype
· Testing frameworks (Jest, Vitest, or Cypress)
','sent','2026-11-09','2026-11-11',NULL,'y-strategie','31dbade20293397aa6b1c43e776afedcfd5edd33e96411cc264be9e678293ba7','{"CDO": "company context (reporting line), not a skill", "Digital": "company context, not a skill", "Transformation": "company context (Digital Transformation Manager title), not a skill", "Manager": "reporting-line title, not a skill", "Developer": "role title, handled by the title check", "Development": "role title, handled by the title check", "Senior": "seniority, handled by the title check", "Front": "role title, covered by the front-end years requirement", "FE": "abbreviation of front end, covered by the years requirement", "Experience": "generic word from ''experience'' wording, not a technology", "jQuery-based": "adjective for the legacy code, covered by the jQuery requirement", "Version": "part of ''Version control Git'', covered by the Git requirement", "UIs": "generic word from the Tailwind line, covered by Tailwind CSS", "Making": "word from the HTML line''s prose, no technology"}');
INSERT INTO "offers" VALUES(6,14,'Software Development Manager','https://careers.oracle.com/en/sites/jobsearch/job/344557/?utm_source=external%20referral&utm_medium=referral','jobs/oracle-software-development-manager-v1','Mohamed-Amine-Sayagh-Software-Development-Manager-Oracle.pdf','https://www.masayagh.com/resume/oracle/Mohamed-Amine-Sayagh-Software-Development-Manager-Oracle.pdf',NULL,NULL,'en',0,'Casablanca, Morocco','same city','Source: https://careers.oracle.com/en/sites/jobsearch/job/344557/?utm_source=external%20referral&utm_medium=referral
Location: Casablanca, Morocco

We are seeking an experienced Software Development Manager to lead and scale a multidisciplinary engineering organization of 30+ engineers at our Morocco Development Center. This leader will be accountable for people leadership, engineering execution, operational excellence, and talent development across work spanning Oracle Support, Oracle Operations, AI data platforms, AI-enabled capabilities, and related software engineering initiatives.

The successful candidate combines strong engineering judgment with a proven ability to lead teams of engineers and senior technical professionals, create clarity across a diverse portfolio, and build an inclusive, high-performing organization.

As a manager of the software engineering division, you will apply your knowledge of software architecture to manage software development tasks associated with developing, debugging or designing software applications, operating systems and databases according to provided design specifications. Build enhancements within an existing software architecture and occasionally suggest improvements to the architecture.
Lead, coach, and develop an engineering organization of 30 or more employees, including engineering managers, technical leads, and individual contributors.
- Set a clear operating model, organizational structure, goals, and priorities that align local execution with broader product, support, data, and AI strategies.

- Deliver reliable, secure, scalable software and operational improvements across assigned initiatives.

- Partner closely with global engineering, product, support, data, security, and operations teams to define roadmaps, resolve dependencies, and deliver measurable outcomes.

- Establish a culture of customer focus and operational excellence, particularly for work supporting Oracle customers and production services.

- Drive engineering best practices, including architecture reviews, design quality, code quality, testing, release readiness, incident management, and post-incident learning.

- Use data to manage delivery health, quality, reliability, customer impact, hiring progress, engagement, and workforce capacity.

- Build and execute talent plans: hiring, onboarding, performance management, career development, succession planning, and retention.

- Develop technical and leadership capability in modern data, cloud, automation, and AI technologies, ensuring practical and responsible adoption.

- Foster an inclusive, collaborative environment that encourages ownership, innovation, continuous improvement, and transparent communication.

- Represent the Morocco Development Center in cross-functional planning, leadership forums, and global stakeholder discussions.

- Manage headcount, staffing plans, budgets, and vendor or partner relationships as applicable.

Required Qualifications
- Bachelor’s degree in Computer Science, Engineering, or a related field, or equivalent practical experience.

- 10+ years of software engineering, systems engineering, data engineering, or related technical experience.

- 5+ years of people-management experience, including experience managing managers and/or leading sizable engineering teams.

- Demonstrated success delivering complex software, platform, support, data, or AI-related initiatives across multiple teams and stakeholders.

- Strong understanding of modern software development practices, cloud services, operational reliability, security, and agile delivery.

- Experience leading teams that support production systems or enterprise customers, including incident response and service improvement.

- Ability to translate business and customer needs into clear technical priorities and executable plans.

- Excellent communication, stakeholder-management, and organizational leadership skills.

- Professional fluency in English; French and/or Arabic are strongly preferred.

Preferred Qualifications
- Experience in enterprise software, cloud infrastructure, developer platforms, data platforms, analytics, machine learning, or generative AI.

- Experience working in a global, distributed engineering organization.

- Experience building or scaling engineering teams in Morocco or the broader EMEA region.

- Familiarity with Oracle products, Oracle Support processes, or enterprise customer environments.

- Experience with workforce planning, organizational design, and budget management.

Career Level - M2
','sent','2026-11-10','2026-11-11',NULL,'oracle','9e065ff4ad4853ace22f595e3515612ee8f1256cc25b91f0eb12336f15971d6f','{"AI-enabled": "product-area description in the intro (Oracle AI-enabled capabilities), not a skill the candidate uses", "AI-related": "appears in the Required line about delivering initiatives; covered by the delivery requirement wording, no tool named", "and/or": "grammar word, not a technology", "Center": "part of the location name ''Morocco Development Center''", "Development": "title and location words, handled by the title check", "Manager": "seniority/title word, handled by the title check", "Operations": "Oracle Operations is a product area in the intro, not a tool", "Software": "title word, handled by the title check", "Morocco": "covered by the Casablanca location requirement", "Support": "part of the product name ''Oracle Support'', covered by Oracle products"}');
INSERT INTO "offers" VALUES(7,14,'Senior AI Software Engineer','https://careers.oracle.com/en/sites/jobsearch/job/338502/?utm_source=external%20referral&utm_medium=referral','jobs/oracle-senior-ai-software-engineer-v1','Mohamed-Amine-Sayagh-Senior-AI-Software-Engineer-Oracle.pdf','https://www.masayagh.com/resume/oracle/Mohamed-Amine-Sayagh-Senior-AI-Software-Engineer-Oracle.pdf',NULL,NULL,'en',0,'Casablanca, Morocco','same city','Source: https://careers.oracle.com/en/sites/jobsearch/job/338502/?utm_source=external%20referral&utm_medium=referral
Location: Casablanca, Morocco

We are looking for a senior engineer with strong coding ability, sound technical judgment, and the ability to lead engineering work from design through delivery. The ideal candidate is comfortable owning complex technical areas, reviewing code, mentoring others, and driving execution across teams.

As a Senior AI Software Engineer at Oracle MADC, you will help build AI capabilities into Oracle products through strong software engineering, technical leadership, and high-quality execution.

This is a software engineering role for someone who can work confidently across large codebases, design reliable systems, and deliver production-ready features at speed. You will contribute to the architecture, implementation, and evolution of AI-enabled product capabilities, working closely with engineering, product, and AI teams.

In this role, you will
- Design, develop, and maintain production-grade software for AI-enabled Oracle products.
- Build scalable services, APIs, SDKs, and reusable platform components.
- Work across large codebases, quickly understanding existing architectures, patterns, and dependencies.
- Translate product and business requirements into practical technical designs and implementation plans.
- Integrate modern AI and Large Language Model capabilities into reliable enterprise software systems.
- Improve system quality across reliability, performance, maintainability, testing, and operational readiness.
- Review technical designs and code changes with strong attention to correctness and long-term impact.
- Lead engineering execution across sprints, including planning, prioritization, task breakdown, and delivery tracking.
- Mentor engineers and help raise engineering standards across the team.

Requirements
- Bachelor’s or Master’s degree in Computer Science, Software Engineering, or a related technical field.
- Strong professional experience in software engineering, preferably in backend, platform, infrastructure, or enterprise product development.
- Proficiency in one or more programming languages such as Java, Python, C++, or similar.
- Strong understanding of data structures, algorithms, system design, and software architecture.
- Experience designing and building production-grade services, APIs, SDKs, libraries, or platform components.
- Ability to work effectively in large, complex codebases and deliver high-quality changes with limited ramp-up time.
- Working knowledge of modern AI systems, Large Language Models, AI application development, or AI platform integration.
- Experience with testing, debugging, performance analysis, CI/CD, and production support practices.
- Strong technical leadership skills, including code review, design review, mentoring, and engineering planning.
- Excellent problem-solving, ownership, communication, and collaboration skills.

Preferred Qualifications
- Experience building AI-enabled enterprise applications or AI platform capabilities.
- Experience with distributed systems, cloud services, or large-scale backend platforms.
- Experience developing developer-facing tools, SDKs, APIs, or internal engineering frameworks.
- Familiarity with LLM orchestration, evaluation, RAG, agentic workflows, observability, or AI governance.
- Prior experience as a technical lead or senior engineer driving execution across multiple contributors.

As a member of the software engineering division, you will assist in defining and developing software for tasks associated with the developing, debugging or designing of software applications or operating systems. Provide technical leadership to other software developers. Specify, design and implement modest changes to existing software architecture to meet changing needs.
Career Level - IC3
','sent','2026-11-10','2026-11-11',NULL,'oracle','9e065ff4ad4853ace22f595e3515612ee8f1256cc25b91f0eb12336f15971d6f','{"MADC": "employer division name, not a skill", "Oracle": "employer name, not a skill", "Senior": "seniority, handled by the title check", "Master": "degree level, covered by the degree requirement on line 17"}');
INSERT INTO "offers" VALUES(8,16,'Senior AI Engineer / Java Spring Boot (H/F)','https://www.linkedin.com/jobs/view/4489607316?_l=en_US','jobs/cgi-senior-ai-engineer-java-spring-boot-h-f-v1','Mohamed-Amine-Sayagh-Senior-AI-Engineer-Java-Spring-Boot-H-F-CGI.pdf','https://www.masayagh.com/resume/cgi/Mohamed-Amine-Sayagh-Senior-AI-Engineer-Java-Spring-Boot-H-F-CGI.pdf',NULL,NULL,'fr',1,'Casablanca, Morocco','same city','Source: https://www.linkedin.com/jobs/view/4489607316?_l=en_US
Location: Casablanca, Morocco

Description de poste

Dans le cadre d''un programme de modernisation d''un système d''encaissement, nous recherchons un Senior AI Engineer pour concevoir, intégrer et déployer des composants et modèles d''intelligence artificielle.

Vous interviendrez sur des problématiques d''intégration de l''IA dans un environnement applicatif complexe, avec un accent particulier sur l''architecture Back-End, les architectures distribuées et la continuité technique du projet.

Fonctions et responsabilités

Concevoir et développer des composants et services intégrant des fonctionnalités d''intelligence artificielle.

Concevoir et implémenter des solutions basées sur l''IA agentique.

Participer au développement et à l''intégration de solutions IA dans un environnement Java / Spring Boot.

Concevoir et faire évoluer des architectures Back-End basées sur les microservices et les architectures event-driven.

Assurer l''intégration des composants IA avec les systèmes existants et les différentes sources de données.

Travailler avec des bases de données relationnelles et documentaires.

Contribuer à la définition des choix d''architecture et garantir la cohérence technique des solutions.

Assurer la qualité, la performance, la sécurité et la maintenabilité des composants développés.

Participer aux revues de code, aux tests techniques et à l''amélioration continue.

Contribuer aux processus d''intégration et de déploiement continus (CI/CD).

Accompagner les équipes techniques et garantir la continuité des développements tout au long du projet.

Qualités requises pour réussir dans ce rôle

Formation supérieure en informatique (Bac+5 ou équivalent).

Minimum 10 ans d''expérience en développement Java / Spring Boot.

Minimum 2 ans d''expérience en AI Building et intégration de solutions d''intelligence artificielle.

Bonne maîtrise des concepts d''IA agentique.

Solide expérience en conception d''architectures Back-End.

Maîtrise des architectures microservices et event-driven.

Bonne connaissance des bases de données relationnelles et documentaires.

Maîtrise des outils Git, CI/CD et des pratiques de tests (Sonar).

Qualités requises

Forte capacité d''analyse et de conception technique.

Autonomie et leadership technique.

Capacité à résoudre des problématiques complexes.

Esprit d''équipe et aisance dans la collaboration transverse.

Rigueur, sens de la qualité et orientation résultats.

CGI est un employeur inclusif et attentif aux candidatures des personnes en situation de handicap et à l’évolution de carrières des hommes et des femmes.

Ensemble, en tant que propriétaires, mettons notre savoir-faire à l’œuvre.

La vie chez CGI est ancrée dans l’actionnariat, le travail d’équipe, le respect et un sentiment d’appartenance. Chez nous, vous pourrez exploiter votre plein potentiel parce que…

Nous vous invitons à devenir propriétaire dès le jour 1 alors que nous travaillons ensemble à faire de notre rêve une réalité. C’est pourquoi nous nous désignons comme associés de CGI, plutôt que comme employés. Nous tirons profit des retombées de notre succès collectif et contribuons activement à l’orientation et à la stratégie de notre entreprise.

Votre travail crée de la valeur. Vous élaborerez des solutions novatrices et développerez des relations durables avec vos collègues et clients, tout en ayant accès à des capacités mondiales pour concrétiser vos idées, saisir de nouvelles opportunités, et bénéficier d’une expertise sectorielle et technologique de pointe.

Vous ferez évoluer votre carrière en vous joignant à une entreprise bâtie pour croître et durer. Vous serez soutenus par des leaders qui ont votre santé et bien-être à cœur et qui vous permettront de saisir des occasions afin de parfaire vos compétences et élargir les horizons.

Ce même engagement envers l’équité s’étend à notre utilisation des technologies. Afin de soutenir notre équipe de recrutement, des outils d’IA peuvent être utilisés pour aider à l’évaluation des candidatures, sans jamais remplacer le jugement humain. Toutes les décisions d’embauche demeurent entièrement entre les mains de nos professionnels du recrutement.

Joignez-vous à nous, l’une des plus importantes entreprises de conseil en technologie de l’information (TI) et en management au monde.
','sent','2026-11-11','2026-11-11',NULL,'cgi','f3335ecb511d9b8dde24a9b92287bb5825b7ebf9084420c6201fceca3ab4a401','{"Bac+5": "degree level, covered by the degree requirement on line 19", "Minimum 10": "covered by the 10+ years years_experience pick", "Minimum 2": "covered by the 2+ years years_experience pick", "Senior": "seniority, handled by the title check", "Engineer": "job title, handled by the title check", "CGI": "company name, not a skill", "Joignez-vous": "company introduction wording", "bien-être": "company culture and benefits line (33 onward), skipped"}');
CREATE TABLE profile (id INTEGER PRIMARY KEY, key TEXT NOT NULL UNIQUE, text_en TEXT NOT NULL, text_fr TEXT);
INSERT INTO "profile" VALUES(1,'summary','Software developer building product experiences that simplify complex processes. Combining engineering, visual design, business understanding, and AI-assisted development to turn inefficient workflows into practical tools that help teams get more done. Looking to join a team that ships products at scale.','Développeur logiciel qui conçoit des expériences produit simplifiant des processus complexes. J''allie ingénierie, design visuel, sens métier et développement assisté par l''IA pour transformer des workflows inefficaces en outils concrets qui rendent les équipes plus efficaces. Je souhaite rejoindre une équipe qui livre des produits à grande échelle.');
INSERT INTO "profile" VALUES(2,'role','Software Engineer','Ingénieur logiciel');
INSERT INTO "profile" VALUES(3,'cover_greeting','Dear Hiring Team,','Madame, Monsieur,');
INSERT INTO "profile" VALUES(4,'cover_closing','Best regards,','');
CREATE TABLE projects (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  tech TEXT NOT NULL,
  link TEXT NOT NULL,
  duration TEXT NOT NULL,
  duration_fr TEXT
, tech_fr TEXT);
INSERT INTO "projects" VALUES(1,'OrbitRows CLI','Python · CLI · AI Agent · SQLite · SQL · JEV · GLiNER2','https://www.masayagh.com/work/orbitrows/','21 working days','21 jours ouvrés','Python · CLI · Agent IA · SQLite · SQL · JEV · GLiNER2');
INSERT INTO "projects" VALUES(2,'LingoWP','WordPress · React · Python · FastAPI · PostgreSQL · FreeBSD','https://www.masayagh.com/work/lingowp/','43 working days','43 jours ouvrés',NULL);
CREATE TABLE requirement_terms (
  requirement_id INTEGER NOT NULL REFERENCES requirements(id),
  term TEXT NOT NULL,
  skill_id INTEGER REFERENCES skills(id),
  PRIMARY KEY (requirement_id, term)
);
INSERT INTO "requirement_terms" VALUES(126,'Casablanca',NULL);
INSERT INTO "requirement_terms" VALUES(127,'informatique',71);
INSERT INTO "requirement_terms" VALUES(129,'Java',25);
INSERT INTO "requirement_terms" VALUES(130,'Spring Boot',50);
INSERT INTO "requirement_terms" VALUES(132,'AI Building',NULL);
INSERT INTO "requirement_terms" VALUES(133,'IA agentique',72);
INSERT INTO "requirement_terms" VALUES(134,'Back-End',NULL);
INSERT INTO "requirement_terms" VALUES(135,'microservices',32);
INSERT INTO "requirement_terms" VALUES(136,'event-driven',NULL);
INSERT INTO "requirement_terms" VALUES(137,'bases de données',74);
INSERT INTO "requirement_terms" VALUES(138,'Git',20);
INSERT INTO "requirement_terms" VALUES(139,'CI/CD',6);
INSERT INTO "requirement_terms" VALUES(140,'Sonar',49);
INSERT INTO "requirement_terms" VALUES(141,'tests',75);
INSERT INTO "requirement_terms" VALUES(142,'conception technique',83);
INSERT INTO "requirement_terms" VALUES(143,'leadership',NULL);
INSERT INTO "requirement_terms" VALUES(144,'problématiques complexes',84);
INSERT INTO "requirement_terms" VALUES(145,'collaboration transverse',85);
INSERT INTO "requirement_terms" VALUES(146,'orientation résultats',86);
INSERT INTO "requirement_terms" VALUES(147,'intelligence artificielle',73);
INSERT INTO "requirement_terms" VALUES(148,'architectures distribuées',76);
INSERT INTO "requirement_terms" VALUES(149,'intelligence artificielle',73);
INSERT INTO "requirement_terms" VALUES(150,'IA agentique',72);
INSERT INTO "requirement_terms" VALUES(151,'Java',25);
INSERT INTO "requirement_terms" VALUES(152,'Spring Boot',50);
INSERT INTO "requirement_terms" VALUES(153,'microservices',32);
INSERT INTO "requirement_terms" VALUES(154,'event-driven',NULL);
INSERT INTO "requirement_terms" VALUES(155,'sources de données',77);
INSERT INTO "requirement_terms" VALUES(156,'bases de données',74);
INSERT INTO "requirement_terms" VALUES(157,'choix d''architecture',78);
INSERT INTO "requirement_terms" VALUES(158,'performance',NULL);
INSERT INTO "requirement_terms" VALUES(159,'sécurité',79);
INSERT INTO "requirement_terms" VALUES(160,'revues de code',9);
INSERT INTO "requirement_terms" VALUES(161,'tests techniques',81);
INSERT INTO "requirement_terms" VALUES(162,'CI/CD',6);
INSERT INTO "requirement_terms" VALUES(163,'équipes techniques',82);
INSERT INTO "requirement_terms" VALUES(164,'Casablanca',NULL);
INSERT INTO "requirement_terms" VALUES(165,'AI Software Engineer',NULL);
INSERT INTO "requirement_terms" VALUES(166,'production-grade software',NULL);
INSERT INTO "requirement_terms" VALUES(167,'APIs',67);
INSERT INTO "requirement_terms" VALUES(167,'SDKs',48);
INSERT INTO "requirement_terms" VALUES(168,'codebases',NULL);
INSERT INTO "requirement_terms" VALUES(169,'Large Language Model',NULL);
INSERT INTO "requirement_terms" VALUES(170,'testing',75);
INSERT INTO "requirement_terms" VALUES(170,'performance',NULL);
INSERT INTO "requirement_terms" VALUES(171,'technical designs',53);
INSERT INTO "requirement_terms" VALUES(172,'engineering execution',NULL);
INSERT INTO "requirement_terms" VALUES(173,'engineering standards',NULL);
INSERT INTO "requirement_terms" VALUES(174,'Computer Science',71);
INSERT INTO "requirement_terms" VALUES(174,'Software Engineering',NULL);
INSERT INTO "requirement_terms" VALUES(175,'software engineering',NULL);
INSERT INTO "requirement_terms" VALUES(176,'backend',NULL);
INSERT INTO "requirement_terms" VALUES(177,'Java',25);
INSERT INTO "requirement_terms" VALUES(177,'Python',43);
INSERT INTO "requirement_terms" VALUES(177,'C++',NULL);
INSERT INTO "requirement_terms" VALUES(178,'data structures',NULL);
INSERT INTO "requirement_terms" VALUES(178,'algorithms',NULL);
INSERT INTO "requirement_terms" VALUES(179,'system design',53);
INSERT INTO "requirement_terms" VALUES(179,'software architecture',NULL);
INSERT INTO "requirement_terms" VALUES(180,'APIs',67);
INSERT INTO "requirement_terms" VALUES(180,'SDKs',48);
INSERT INTO "requirement_terms" VALUES(180,'libraries',NULL);
INSERT INTO "requirement_terms" VALUES(181,'codebases',NULL);
INSERT INTO "requirement_terms" VALUES(182,'AI systems',NULL);
INSERT INTO "requirement_terms" VALUES(182,'Large Language Models',NULL);
INSERT INTO "requirement_terms" VALUES(182,'AI application development',NULL);
INSERT INTO "requirement_terms" VALUES(183,'CI/CD',6);
INSERT INTO "requirement_terms" VALUES(184,'testing',75);
INSERT INTO "requirement_terms" VALUES(184,'debugging',NULL);
INSERT INTO "requirement_terms" VALUES(184,'performance analysis',NULL);
INSERT INTO "requirement_terms" VALUES(185,'technical leadership',NULL);
INSERT INTO "requirement_terms" VALUES(186,'code review',9);
INSERT INTO "requirement_terms" VALUES(187,'design review',NULL);
INSERT INTO "requirement_terms" VALUES(188,'mentoring',NULL);
INSERT INTO "requirement_terms" VALUES(189,'engineering planning',NULL);
INSERT INTO "requirement_terms" VALUES(190,'problem-solving',NULL);
INSERT INTO "requirement_terms" VALUES(191,'communication',NULL);
INSERT INTO "requirement_terms" VALUES(192,'AI-enabled',NULL);
INSERT INTO "requirement_terms" VALUES(193,'distributed systems',76);
INSERT INTO "requirement_terms" VALUES(193,'cloud services',NULL);
INSERT INTO "requirement_terms" VALUES(194,'SDKs',48);
INSERT INTO "requirement_terms" VALUES(194,'APIs',67);
INSERT INTO "requirement_terms" VALUES(195,'RAG',44);
INSERT INTO "requirement_terms" VALUES(195,'LLM orchestration',NULL);
INSERT INTO "requirement_terms" VALUES(195,'agentic workflows',72);
INSERT INTO "requirement_terms" VALUES(196,'observability',NULL);
INSERT INTO "requirement_terms" VALUES(196,'AI governance',NULL);
INSERT INTO "requirement_terms" VALUES(197,'technical lead',NULL);
INSERT INTO "requirement_terms" VALUES(198,'full-stack',NULL);
INSERT INTO "requirement_terms" VALUES(199,'front-end',NULL);
INSERT INTO "requirement_terms" VALUES(200,'APIs',67);
INSERT INTO "requirement_terms" VALUES(201,'data integration',13);
INSERT INTO "requirement_terms" VALUES(202,'cloud',NULL);
INSERT INTO "requirement_terms" VALUES(203,'hiring',NULL);
INSERT INTO "requirement_terms" VALUES(203,'coaching',NULL);
INSERT INTO "requirement_terms" VALUES(204,'managing teams',NULL);
INSERT INTO "requirement_terms" VALUES(204,'matrixed',NULL);
INSERT INTO "requirement_terms" VALUES(205,'enterprise software',NULL);
INSERT INTO "requirement_terms" VALUES(205,'developer platforms',NULL);
INSERT INTO "requirement_terms" VALUES(205,'frameworks',NULL);
INSERT INTO "requirement_terms" VALUES(206,'engineering standards',NULL);
INSERT INTO "requirement_terms" VALUES(207,'communication',NULL);
INSERT INTO "requirement_terms" VALUES(208,'computer science',71);
INSERT INTO "requirement_terms" VALUES(209,'AI-enabled products',NULL);
INSERT INTO "requirement_terms" VALUES(209,'agentic systems',72);
INSERT INTO "requirement_terms" VALUES(209,'AI-assisted developer tools',NULL);
INSERT INTO "requirement_terms" VALUES(210,'Large language models',NULL);
INSERT INTO "requirement_terms" VALUES(210,'agent orchestration',NULL);
INSERT INTO "requirement_terms" VALUES(211,'SDKs',48);
INSERT INTO "requirement_terms" VALUES(211,'developer tools',NULL);
INSERT INTO "requirement_terms" VALUES(212,'distributed',NULL);
INSERT INTO "requirement_terms" VALUES(212,'multicultural',NULL);
INSERT INTO "requirement_terms" VALUES(213,'site reliability engineering',NULL);
INSERT INTO "requirement_terms" VALUES(213,'incident management',NULL);
INSERT INTO "requirement_terms" VALUES(214,'Master’s degree',NULL);
INSERT INTO "requirement_terms" VALUES(215,'testing',75);
INSERT INTO "requirement_terms" VALUES(215,'observability',NULL);
INSERT INTO "requirement_terms" VALUES(216,'distributed systems',76);
INSERT INTO "requirement_terms" VALUES(217,'Morocco',NULL);
INSERT INTO "requirement_terms" VALUES(218,'Casablanca',NULL);
INSERT INTO "requirement_terms" VALUES(219,'Computer Science',71);
INSERT INTO "requirement_terms" VALUES(221,'people-management',NULL);
INSERT INTO "requirement_terms" VALUES(222,'managing managers',NULL);
INSERT INTO "requirement_terms" VALUES(223,'complex software',NULL);
INSERT INTO "requirement_terms" VALUES(224,'stakeholders',NULL);
INSERT INTO "requirement_terms" VALUES(225,'cloud services',NULL);
INSERT INTO "requirement_terms" VALUES(226,'agile',NULL);
INSERT INTO "requirement_terms" VALUES(227,'security',79);
INSERT INTO "requirement_terms" VALUES(228,'operational reliability',NULL);
INSERT INTO "requirement_terms" VALUES(229,'production systems',NULL);
INSERT INTO "requirement_terms" VALUES(230,'enterprise customers',NULL);
INSERT INTO "requirement_terms" VALUES(231,'incident response',NULL);
INSERT INTO "requirement_terms" VALUES(232,'technical priorities',NULL);
INSERT INTO "requirement_terms" VALUES(233,'communication',NULL);
INSERT INTO "requirement_terms" VALUES(234,'stakeholder-management',NULL);
INSERT INTO "requirement_terms" VALUES(235,'organizational leadership',NULL);
INSERT INTO "requirement_terms" VALUES(236,'English',NULL);
INSERT INTO "requirement_terms" VALUES(237,'French',NULL);
INSERT INTO "requirement_terms" VALUES(237,'Arabic',NULL);
INSERT INTO "requirement_terms" VALUES(238,'coach',NULL);
INSERT INTO "requirement_terms" VALUES(239,'roadmaps',NULL);
INSERT INTO "requirement_terms" VALUES(240,'architecture reviews',NULL);
INSERT INTO "requirement_terms" VALUES(241,'code quality',NULL);
INSERT INTO "requirement_terms" VALUES(241,'testing',75);
INSERT INTO "requirement_terms" VALUES(242,'incident management',NULL);
INSERT INTO "requirement_terms" VALUES(243,'hiring',NULL);
INSERT INTO "requirement_terms" VALUES(244,'performance management',NULL);
INSERT INTO "requirement_terms" VALUES(245,'cloud',NULL);
INSERT INTO "requirement_terms" VALUES(245,'automation',NULL);
INSERT INTO "requirement_terms" VALUES(245,'AI',73);
INSERT INTO "requirement_terms" VALUES(246,'budgets',NULL);
INSERT INTO "requirement_terms" VALUES(247,'enterprise software',NULL);
INSERT INTO "requirement_terms" VALUES(248,'developer platforms',NULL);
INSERT INTO "requirement_terms" VALUES(248,'data platforms',NULL);
INSERT INTO "requirement_terms" VALUES(249,'machine learning',NULL);
INSERT INTO "requirement_terms" VALUES(249,'generative AI',NULL);
INSERT INTO "requirement_terms" VALUES(250,'distributed engineering',NULL);
INSERT INTO "requirement_terms" VALUES(251,'EMEA',NULL);
INSERT INTO "requirement_terms" VALUES(252,'Oracle products',NULL);
INSERT INTO "requirement_terms" VALUES(253,'workforce planning',NULL);
INSERT INTO "requirement_terms" VALUES(253,'budget management',NULL);
INSERT INTO "requirement_terms" VALUES(255,'Vue 3',60);
INSERT INTO "requirement_terms" VALUES(256,'composition API',NULL);
INSERT INTO "requirement_terms" VALUES(257,'Tailwind CSS',54);
INSERT INTO "requirement_terms" VALUES(258,'HTML',23);
INSERT INTO "requirement_terms" VALUES(259,'accessible',NULL);
INSERT INTO "requirement_terms" VALUES(260,'component libraries',NULL);
INSERT INTO "requirement_terms" VALUES(260,'design systems',NULL);
INSERT INTO "requirement_terms" VALUES(261,'Laravel',29);
INSERT INTO "requirement_terms" VALUES(261,'Blade',5);
INSERT INTO "requirement_terms" VALUES(262,'API',67);
INSERT INTO "requirement_terms" VALUES(263,'jQuery',28);
INSERT INTO "requirement_terms" VALUES(264,'Coaching',NULL);
INSERT INTO "requirement_terms" VALUES(264,'mentoring',NULL);
INSERT INTO "requirement_terms" VALUES(265,'JavaScript',26);
INSERT INTO "requirement_terms" VALUES(266,'ES6',NULL);
INSERT INTO "requirement_terms" VALUES(267,'TypeScript',56);
INSERT INTO "requirement_terms" VALUES(268,'HTML5',23);
INSERT INTO "requirement_terms" VALUES(269,'CSS',11);
INSERT INTO "requirement_terms" VALUES(269,'SCSS',47);
INSERT INTO "requirement_terms" VALUES(269,'SASS',47);
INSERT INTO "requirement_terms" VALUES(270,'Git',20);
INSERT INTO "requirement_terms" VALUES(271,'CI/CD',6);
INSERT INTO "requirement_terms" VALUES(272,'performance optimisation',NULL);
INSERT INTO "requirement_terms" VALUES(273,'Laravel Mix',NULL);
INSERT INTO "requirement_terms" VALUES(273,'Vite',58);
INSERT INTO "requirement_terms" VALUES(273,'Sanctum',NULL);
INSERT INTO "requirement_terms" VALUES(274,'Docker',15);
INSERT INTO "requirement_terms" VALUES(274,'WAMP',NULL);
INSERT INTO "requirement_terms" VALUES(274,'LAMP',NULL);
INSERT INTO "requirement_terms" VALUES(275,'API endpoints',NULL);
INSERT INTO "requirement_terms" VALUES(276,'Pinia',40);
INSERT INTO "requirement_terms" VALUES(276,'state management',NULL);
INSERT INTO "requirement_terms" VALUES(277,'VeeValidate',NULL);
INSERT INTO "requirement_terms" VALUES(278,'Accessibility',1);
INSERT INTO "requirement_terms" VALUES(278,'WCAG',1);
INSERT INTO "requirement_terms" VALUES(279,'Maizzle',NULL);
INSERT INTO "requirement_terms" VALUES(280,'AI/ML',NULL);
INSERT INTO "requirement_terms" VALUES(281,'UI Design',57);
INSERT INTO "requirement_terms" VALUES(282,'UX',NULL);
INSERT INTO "requirement_terms" VALUES(283,'prototype',70);
INSERT INTO "requirement_terms" VALUES(284,'Jest',27);
INSERT INTO "requirement_terms" VALUES(284,'Vitest',59);
INSERT INTO "requirement_terms" VALUES(284,'Cypress',12);
INSERT INTO "requirement_terms" VALUES(285,'jQuery',28);
INSERT INTO "requirement_terms" VALUES(285,'Vue 3',60);
INSERT INTO "requirement_terms" VALUES(286,'component library',NULL);
INSERT INTO "requirement_terms" VALUES(287,'accessibility',1);
INSERT INTO "requirement_terms" VALUES(287,'performance',NULL);
INSERT INTO "requirement_terms" VALUES(288,'Casablanca',NULL);
CREATE TABLE requirements (
  id INTEGER PRIMARY KEY,
  offer_id INTEGER NOT NULL REFERENCES offers(id),
  section TEXT NOT NULL,
  priority TEXT NOT NULL CHECK (priority IN ('must_have', 'preferred')),
  quote TEXT NOT NULL,
  description TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('evidence', 'years_experience')),
  min_years REAL,
  targets TEXT,
  reviewed INTEGER NOT NULL DEFAULT 0,
  note TEXT,
  override_status TEXT,
  override_reason TEXT
, override_quote TEXT);
INSERT INTO "requirements" VALUES(126,8,'location','must_have','Location: Casablanca, Morocco','Role based in Casablanca, Morocco','evidence',NULL,'summary',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(127,8,'requirement','must_have','Formation supérieure en informatique (Bac+5 ou équivalent).','Higher education in computer science (Bac+5 or equivalent)','evidence',NULL,'summary',0,'Degree line; French field term ''informatique'' is mapped to English separately.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(128,8,'requirement','must_have','Minimum 10 ans d''expérience en développement Java / Spring Boot.','10+ years of Java / Spring Boot development','years_experience',10.0,NULL,0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(129,8,'requirement','must_have','Minimum 10 ans d''expérience en développement Java / Spring Boot.','Java development experience','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(130,8,'requirement','must_have','Minimum 10 ans d''expérience en développement Java / Spring Boot.','Spring Boot development experience','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(131,8,'requirement','must_have','Minimum 2 ans d''expérience en AI Building et intégration de solutions d''intelligence artificielle.','2+ years of AI building and AI solution integration','years_experience',2.0,NULL,0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(132,8,'requirement','must_have','Minimum 2 ans d''expérience en AI Building et intégration de solutions d''intelligence artificielle.','AI building and integration of AI solutions','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(133,8,'requirement','must_have','Bonne maîtrise des concepts d''IA agentique.','Solid grasp of agentic AI concepts','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(134,8,'requirement','must_have','Solide expérience en conception d''architectures Back-End.','Solid experience designing Back-End architectures','evidence',NULL,'experience,summary',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(135,8,'requirement','must_have','Maîtrise des architectures microservices et event-driven.','Microservices architecture expertise','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(136,8,'requirement','must_have','Maîtrise des architectures microservices et event-driven.','Event-driven architecture expertise','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(137,8,'requirement','must_have','Bonne connaissance des bases de données relationnelles et documentaires.','Relational databases (documentaires part noted)','evidence',NULL,'skills,experience',0,'Line also asks for document databases (''et documentaires''); that word alone is too generic to be a search term, so only the relational half is picked.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(138,8,'requirement','must_have','Maîtrise des outils Git, CI/CD et des pratiques de tests (Sonar).','Git','evidence',NULL,'skills',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(139,8,'requirement','must_have','Maîtrise des outils Git, CI/CD et des pratiques de tests (Sonar).','CI/CD tooling','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(140,8,'requirement','must_have','Maîtrise des outils Git, CI/CD et des pratiques de tests (Sonar).','SonarQube code quality tooling','evidence',NULL,'skills',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(141,8,'requirement','must_have','Maîtrise des outils Git, CI/CD et des pratiques de tests (Sonar).','Testing practices','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(142,8,'requirement','preferred','Forte capacité d''analyse et de conception technique.','Strong technical analysis and design','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(143,8,'requirement','preferred','Autonomie et leadership technique.','Technical leadership and autonomy','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(144,8,'requirement','preferred','Capacité à résoudre des problématiques complexes.','Solving complex problems','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(145,8,'requirement','preferred','Esprit d''équipe et aisance dans la collaboration transverse.','Cross-functional collaboration','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(146,8,'requirement','preferred','Rigueur, sens de la qualité et orientation résultats.','Quality focus and results orientation','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(147,8,'responsibility','preferred','Dans le cadre d''un programme de modernisation d''un système d''encaissement, nous recherchons un Senior AI Engineer pour concevoir, intégrer et déployer des composants et modèles d''intelligence artificielle.','Design, integrate and deploy AI components and models','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(148,8,'responsibility','preferred','Vous interviendrez sur des problématiques d''intégration de l''IA dans un environnement applicatif complexe, avec un accent particulier sur l''architecture Back-End, les architectures distribuées et la continuité technique du projet.','Distributed architectures and AI integration in a complex application environment','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(149,8,'responsibility','preferred','Concevoir et développer des composants et services intégrant des fonctionnalités d''intelligence artificielle.','Build components and services with AI features','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(150,8,'responsibility','preferred','Concevoir et implémenter des solutions basées sur l''IA agentique.','Design and implement agentic AI solutions','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(151,8,'responsibility','preferred','Participer au développement et à l''intégration de solutions IA dans un environnement Java / Spring Boot.','AI solutions in a Java environment','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(152,8,'responsibility','preferred','Participer au développement et à l''intégration de solutions IA dans un environnement Java / Spring Boot.','AI solutions in a Spring Boot environment','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(153,8,'responsibility','preferred','Concevoir et faire évoluer des architectures Back-End basées sur les microservices et les architectures event-driven.','Evolve microservices and event-driven Back-End architectures','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(154,8,'responsibility','preferred','Concevoir et faire évoluer des architectures Back-End basées sur les microservices et les architectures event-driven.','Evolve event-driven Back-End architectures','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(155,8,'responsibility','preferred','Assurer l''intégration des composants IA avec les systèmes existants et les différentes sources de données.','Integrate AI components with existing systems and data sources','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(156,8,'responsibility','preferred','Travailler avec des bases de données relationnelles et documentaires.','Work with relational and document databases','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(157,8,'responsibility','preferred','Contribuer à la définition des choix d''architecture et garantir la cohérence technique des solutions.','Shape architecture decisions and technical consistency','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(158,8,'responsibility','preferred','Assurer la qualité, la performance, la sécurité et la maintenabilité des composants développés.','Quality, performance and maintainability of components','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(159,8,'responsibility','preferred','Assurer la qualité, la performance, la sécurité et la maintenabilité des composants développés.','Security of developed components','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(160,8,'responsibility','preferred','Participer aux revues de code, aux tests techniques et à l''amélioration continue.','Code reviews','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(161,8,'responsibility','preferred','Participer aux revues de code, aux tests techniques et à l''amélioration continue.','Technical testing','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(162,8,'responsibility','preferred','Contribuer aux processus d''intégration et de déploiement continus (CI/CD).','Continuous integration and deployment (CI/CD)','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(163,8,'responsibility','preferred','Accompagner les équipes techniques et garantir la continuité des développements tout au long du projet.','Support technical teams and project continuity','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(164,7,'location','must_have','Location: Casablanca, Morocco','Role based in Casablanca, Morocco','evidence',NULL,'summary',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(165,7,'responsibility','preferred','As a Senior AI Software Engineer at Oracle MADC, you will help build AI capabilities into Oracle products through strong software engineering, technical leadership, and high-quality execution.','Senior AI Software Engineer role on Oracle MADC','evidence',NULL,'summary',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(166,7,'responsibility','preferred','Design, develop, and maintain production-grade software for AI-enabled Oracle products.','Design, develop and maintain production-grade software','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(167,7,'responsibility','preferred','Build scalable services, APIs, SDKs, and reusable platform components.','Build scalable services, APIs and SDKs','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(168,7,'responsibility','preferred','Work across large codebases, quickly understanding existing architectures, patterns, and dependencies.','Work across large codebases','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(169,7,'responsibility','preferred','Integrate modern AI and Large Language Model capabilities into reliable enterprise software systems.','Integrate LLM capabilities into enterprise software','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(170,7,'responsibility','preferred','Improve system quality across reliability, performance, maintainability, testing, and operational readiness.','Improve reliability, performance, maintainability and testing','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(171,7,'responsibility','preferred','Review technical designs and code changes with strong attention to correctness and long-term impact.','Review technical designs and code changes','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(172,7,'responsibility','preferred','Lead engineering execution across sprints, including planning, prioritization, task breakdown, and delivery tracking.','Lead engineering execution across sprints','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(173,7,'responsibility','preferred','Mentor engineers and help raise engineering standards across the team.','Raise engineering standards','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(174,7,'requirement','must_have','Bachelor’s or Master’s degree in Computer Science, Software Engineering, or a related technical field.','Bachelor''s or Master''s degree in Computer Science, Software Engineering or related field','evidence',NULL,'summary',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(175,7,'preferred','preferred','Strong professional experience in software engineering, preferably in backend, platform, infrastructure, or enterprise product development.','Strong professional software engineering experience','evidence',NULL,'experience,summary',0,'Line says ''Strong ... experience'' but also ''preferably'' for the domain; treated as preferred because the line uses soft wording.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(176,7,'preferred','preferred','Strong professional experience in software engineering, preferably in backend, platform, infrastructure, or enterprise product development.','Backend, platform or enterprise product background','evidence',NULL,'summary,experience',0,'Line says ''Strong ... experience'' but also ''preferably'' for the domain; treated as preferred because the line uses soft wording.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(177,7,'requirement','must_have','Proficiency in one or more programming languages such as Java, Python, C++, or similar.','Proficiency in one or more programming languages (Java, Python, C++)','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(178,7,'requirement','must_have','Strong understanding of data structures, algorithms, system design, and software architecture.','Strong understanding of data structures and algorithms','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(179,7,'requirement','must_have','Strong understanding of data structures, algorithms, system design, and software architecture.','Strong understanding of system design and software architecture','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(180,7,'requirement','must_have','Experience designing and building production-grade services, APIs, SDKs, libraries, or platform components.','Built production-grade services, APIs, SDKs or libraries','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(181,7,'requirement','must_have','Ability to work effectively in large, complex codebases and deliver high-quality changes with limited ramp-up time.','Works effectively in large, complex codebases','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(182,7,'requirement','must_have','Working knowledge of modern AI systems, Large Language Models, AI application development, or AI platform integration.','Working knowledge of AI systems and LLMs','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(183,7,'requirement','must_have','Experience with testing, debugging, performance analysis, CI/CD, and production support practices.','CI/CD practices','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(184,7,'requirement','must_have','Experience with testing, debugging, performance analysis, CI/CD, and production support practices.','Testing, debugging and performance analysis in production support','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(185,7,'requirement','must_have','Strong technical leadership skills, including code review, design review, mentoring, and engineering planning.','Strong technical leadership skills','evidence',NULL,'summary,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(186,7,'requirement','must_have','Strong technical leadership skills, including code review, design review, mentoring, and engineering planning.','Code review','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(187,7,'requirement','must_have','Strong technical leadership skills, including code review, design review, mentoring, and engineering planning.','Design review','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(188,7,'requirement','must_have','Strong technical leadership skills, including code review, design review, mentoring, and engineering planning.','Mentoring engineers','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(189,7,'requirement','must_have','Strong technical leadership skills, including code review, design review, mentoring, and engineering planning.','Engineering planning','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(190,7,'requirement','must_have','Excellent problem-solving, ownership, communication, and collaboration skills.','Excellent problem-solving and ownership','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(191,7,'requirement','must_have','Excellent problem-solving, ownership, communication, and collaboration skills.','Excellent communication and collaboration','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(192,7,'preferred','preferred','Experience building AI-enabled enterprise applications or AI platform capabilities.','Building AI-enabled enterprise applications or AI platform capabilities','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(193,7,'preferred','preferred','Experience with distributed systems, cloud services, or large-scale backend platforms.','Distributed systems, cloud services or large-scale backend platforms','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(194,7,'preferred','preferred','Experience developing developer-facing tools, SDKs, APIs, or internal engineering frameworks.','Developer-facing tools, SDKs, APIs or internal engineering frameworks','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(195,7,'preferred','preferred','Familiarity with LLM orchestration, evaluation, RAG, agentic workflows, observability, or AI governance.','Familiarity with LLM orchestration, RAG or agentic workflows','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(196,7,'preferred','preferred','Familiarity with LLM orchestration, evaluation, RAG, agentic workflows, observability, or AI governance.','Familiarity with observability or AI governance','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(197,7,'preferred','preferred','Prior experience as a technical lead or senior engineer driving execution across multiple contributors.','Prior experience as a technical lead or senior engineer','evidence',NULL,'summary,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(198,4,'requirement','must_have','Strong full-stack software development expertise, including modern front-end technologies, service development, APIs, data integration and cloud-based application architectures.','Full-stack development expertise','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(199,4,'requirement','must_have','Strong full-stack software development expertise, including modern front-end technologies, service development, APIs, data integration and cloud-based application architectures.','Modern front-end technologies','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(200,4,'requirement','must_have','Strong full-stack software development expertise, including modern front-end technologies, service development, APIs, data integration and cloud-based application architectures.','APIs and service development','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(201,4,'requirement','must_have','Strong full-stack software development expertise, including modern front-end technologies, service development, APIs, data integration and cloud-based application architectures.','Data integration','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(202,4,'requirement','must_have','Strong full-stack software development expertise, including modern front-end technologies, service development, APIs, data integration and cloud-based application architectures.','Cloud-based application architectures','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(203,4,'requirement','must_have','Experience hiring, developing, coaching and retaining high-performing software engineers.','Hiring, coaching and retaining engineers','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(204,4,'requirement','must_have','Demonstrated success managing teams in a matrixed organisation, with shared accountability across functional and delivery leaders.','Managing teams in a matrixed organisation','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(205,4,'requirement','must_have','Experience delivering enterprise software, cloud services, developer platforms, frameworks or shared engineering capabilities.','Delivering enterprise software, cloud services or developer platforms','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(206,4,'requirement','must_have','Experience establishing and improving engineering standards and practices.','Establishing engineering standards and practices','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(207,4,'requirement','must_have','Strong written and verbal communication skills, with the ability to explain complex technical and organisational topics clearly.','Strong written and verbal communication','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(208,4,'requirement','must_have','Bachelor’s degree in computer science, engineering or a related technical field, or equivalent practical experience.','Bachelor''s in CS/engineering or equivalent practical experience','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(209,4,'preferred','preferred','Building AI-enabled products, agentic systems, generative AI platforms or AI-assisted developer tools.','AI-enabled products, agentic systems, AI-assisted developer tools','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(210,4,'preferred','preferred','Large language models, agent orchestration, prompt and context management, model evaluation, AI guardrails, feedback systems or AI observability.','LLMs and agent orchestration','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(211,4,'preferred','preferred','Building reusable SDKs, frameworks, APIs, developer tools or internal engineering platforms.','Reusable SDKs, frameworks, developer tools','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(212,4,'preferred','preferred','Managing geographically distributed or multicultural engineering teams.','Managing distributed or multicultural teams','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(213,4,'preferred','preferred','Service management, site reliability engineering, incident management or operational readiness.','SRE, incident management, operational readiness','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(214,4,'preferred','preferred','Master’s degree in computer science, engineering, business administration or a related discipline.','Master''s degree in CS, engineering or business','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(215,4,'responsibility','preferred','Establish strong engineering standards across architecture, APIs, testing, observability, reliability and software development.','Engineering standards incl. testing and observability','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(216,4,'responsibility','preferred','Help teams solve complex technical issues across distributed systems and services.','Solve issues across distributed systems','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(217,4,'location','must_have','We are looking for a Senior Manager of Software Development to build, lead and develop a multidisciplinary engineering team in Morocco.','Role based in Morocco','evidence',NULL,NULL,1,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(218,6,'location','must_have','Location: Casablanca, Morocco','Role based in Casablanca','evidence',NULL,NULL,0,'On-site role; location kept must-have.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(219,6,'requirement','must_have','Bachelor’s degree in Computer Science, Engineering, or a related field, or equivalent practical experience.','Bachelor''s in CS/engineering or equivalent practical experience','evidence',NULL,'summary',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(220,6,'requirement','must_have','10+ years of software engineering, systems engineering, data engineering, or related technical experience.','10+ years of software engineering','years_experience',10.0,NULL,0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(221,6,'requirement','must_have','5+ years of people-management experience, including experience managing managers and/or leading sizable engineering teams.','5+ years of people management','evidence',NULL,'experience',0,'Manager years can''t be computed from dates; matched on the term.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(222,6,'requirement','must_have','5+ years of people-management experience, including experience managing managers and/or leading sizable engineering teams.','Managing managers or sizable teams','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(223,6,'requirement','must_have','Demonstrated success delivering complex software, platform, support, data, or AI-related initiatives across multiple teams and stakeholders.','Delivering complex initiatives across teams','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(224,6,'requirement','must_have','Demonstrated success delivering complex software, platform, support, data, or AI-related initiatives across multiple teams and stakeholders.','Delivery across multiple teams and stakeholders','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(225,6,'requirement','must_have','Strong understanding of modern software development practices, cloud services, operational reliability, security, and agile delivery.','Cloud services','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(226,6,'requirement','must_have','Strong understanding of modern software development practices, cloud services, operational reliability, security, and agile delivery.','Agile delivery','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(227,6,'requirement','must_have','Strong understanding of modern software development practices, cloud services, operational reliability, security, and agile delivery.','Security','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(228,6,'requirement','must_have','Strong understanding of modern software development practices, cloud services, operational reliability, security, and agile delivery.','Operational reliability','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(229,6,'requirement','must_have','Experience leading teams that support production systems or enterprise customers, including incident response and service improvement.','Leading teams supporting production systems','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(230,6,'requirement','must_have','Experience leading teams that support production systems or enterprise customers, including incident response and service improvement.','Supporting enterprise customers','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(231,6,'requirement','must_have','Experience leading teams that support production systems or enterprise customers, including incident response and service improvement.','Incident response','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(232,6,'requirement','must_have','Ability to translate business and customer needs into clear technical priorities and executable plans.','Turning business needs into technical priorities','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(233,6,'requirement','must_have','Excellent communication, stakeholder-management, and organizational leadership skills.','Communication','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(234,6,'requirement','must_have','Excellent communication, stakeholder-management, and organizational leadership skills.','Stakeholder management','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(235,6,'requirement','must_have','Excellent communication, stakeholder-management, and organizational leadership skills.','Organizational leadership','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(236,6,'requirement','preferred','Professional fluency in English; French and/or Arabic are strongly preferred.','Professional English','evidence',NULL,'summary',0,'Required by the posting, but the line also says ''strongly preferred'', which the validator won''t mark must-have; English is on the resume anyway.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(237,6,'requirement','preferred','Professional fluency in English; French and/or Arabic are strongly preferred.','French and/or Arabic','evidence',NULL,'summary',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(238,6,'responsibility','preferred','Lead, coach, and develop an engineering organization of 30 or more employees, including engineering managers, technical leads, and individual contributors.','Lead and coach an engineering organization','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(239,6,'responsibility','preferred','Partner closely with global engineering, product, support, data, security, and operations teams to define roadmaps, resolve dependencies, and deliver measurable outcomes.','Define roadmaps with global teams','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(240,6,'responsibility','preferred','Drive engineering best practices, including architecture reviews, design quality, code quality, testing, release readiness, incident management, and post-incident learning.','Architecture reviews','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(241,6,'responsibility','preferred','Drive engineering best practices, including architecture reviews, design quality, code quality, testing, release readiness, incident management, and post-incident learning.','Code quality and testing','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(242,6,'responsibility','preferred','Drive engineering best practices, including architecture reviews, design quality, code quality, testing, release readiness, incident management, and post-incident learning.','Incident management','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(243,6,'responsibility','preferred','Build and execute talent plans: hiring, onboarding, performance management, career development, succession planning, and retention.','Hiring','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(244,6,'responsibility','preferred','Build and execute talent plans: hiring, onboarding, performance management, career development, succession planning, and retention.','Performance management','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(245,6,'responsibility','preferred','Develop technical and leadership capability in modern data, cloud, automation, and AI technologies, ensuring practical and responsible adoption.','Data, cloud, automation and AI capability','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(246,6,'responsibility','preferred','Manage headcount, staffing plans, budgets, and vendor or partner relationships as applicable.','Headcount, staffing and budgets','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(247,6,'preferred','preferred','Experience in enterprise software, cloud infrastructure, developer platforms, data platforms, analytics, machine learning, or generative AI.','Enterprise software','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(248,6,'preferred','preferred','Experience in enterprise software, cloud infrastructure, developer platforms, data platforms, analytics, machine learning, or generative AI.','Developer or data platforms','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(249,6,'preferred','preferred','Experience in enterprise software, cloud infrastructure, developer platforms, data platforms, analytics, machine learning, or generative AI.','Machine learning or generative AI','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(250,6,'preferred','preferred','Experience working in a global, distributed engineering organization.','Global distributed engineering organization','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(251,6,'preferred','preferred','Experience building or scaling engineering teams in Morocco or the broader EMEA region.','Building teams in Morocco or EMEA','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(252,6,'preferred','preferred','Familiarity with Oracle products, Oracle Support processes, or enterprise customer environments.','Familiarity with Oracle products','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(253,6,'preferred','preferred','Experience with workforce planning, organizational design, and budget management.','Workforce planning and budget management','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(254,5,'requirement','must_have','5+ years of professional front end development experience','5+ years of front-end development','years_experience',5.0,NULL,0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(255,5,'requirement','must_have','2+ years working with Vue 3 composition API in production applications','Vue 3 in production','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(256,5,'requirement','must_have','2+ years working with Vue 3 composition API in production applications','Vue composition API in production','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(257,5,'requirement','must_have','Strong Tailwind CSS skills building responsive, maintainable UIs at scale','Tailwind CSS for responsive UIs at scale','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(258,5,'requirement','must_have','Strong understanding of HTML markup Making sure the HTML is valid, confirms wc3 rules and is accessible for users.','Strong HTML markup, valid per W3C rules','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(259,5,'requirement','must_have','Strong understanding of HTML markup Making sure the HTML is valid, confirms wc3 rules and is accessible for users.','Accessible markup for users','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(260,5,'requirement','must_have','Proven experience creating reusable component libraries or design systems','Reusable component libraries or design systems','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(261,5,'requirement','must_have','Laravel Blade templating experience you''ll need to navigate and enhance existing Blade views','Laravel Blade templating','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(262,5,'requirement','must_have','API development - comfortable writing Laravel endpoints or strong ability to collaborate with backend developers on API design','API development with Laravel endpoints or API design with backend team','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(263,5,'requirement','must_have','jQuery experience you''ll be migrating it, so you need to understand what you''re replacing','jQuery experience (legacy code being migrated)','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(264,5,'requirement','must_have','Coaching or mentoring experience supporting junior to mid-level developers','Coaching or mentoring junior to mid-level developers','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(265,5,'requirement','preferred','JavaScript/TypeScript (ES6+)','JavaScript (ES6+)','evidence',NULL,'skills,experience',0,'Under ''Technical Skills'' with no must/required wording, so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(266,5,'requirement','preferred','JavaScript/TypeScript (ES6+)','ES6+ syntax','evidence',NULL,'skills',0,'Under ''Technical Skills'', so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(267,5,'requirement','preferred','JavaScript/TypeScript (ES6+)','TypeScript','evidence',NULL,'skills,experience',0,'Under ''Technical Skills'' with no must/required wording, so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(268,5,'requirement','preferred','HTML5 and modern CSS/SCSS/SASS','HTML5','evidence',NULL,'skills',0,'Under ''Technical Skills'', so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(269,5,'requirement','preferred','HTML5 and modern CSS/SCSS/SASS','Modern CSS, SCSS or SASS','evidence',NULL,'skills',0,'Under ''Technical Skills'', so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(270,5,'requirement','preferred','Using Version control Git (how to merge, resolve merge conflicts and create and push branches)','Git: merge, conflict resolution, branching','evidence',NULL,'skills,experience',0,'Under ''Technical Skills'', so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(271,5,'requirement','preferred','Git workflow and CI/CD basics','CI/CD basics','evidence',NULL,'skills',0,'Under ''Technical Skills'', so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(272,5,'requirement','preferred','Understanding of performance optimisation techniques','Performance optimisation techniques','evidence',NULL,'experience',0,'Under ''Technical Skills'', so preferred.',NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(273,5,'preferred','preferred','Experience with Laravel ecosystem (e.g., Laravel Mix, Vite, Sanctum)','Laravel ecosystem (Laravel Mix, Vite, Sanctum)','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(274,5,'preferred','preferred','Docker/ WAMP/LAMP','Docker or WAMP/LAMP','evidence',NULL,'skills',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(275,5,'preferred','preferred','Able to write and maintain API endpoints to support front end functionality','Writing and maintaining API endpoints for front end','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(276,5,'preferred','preferred','Pinia or other Vue state management','Pinia or other Vue state management','evidence',NULL,'skills',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(277,5,'preferred','preferred','VeeValidate','VeeValidate','evidence',NULL,'skills',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(278,5,'preferred','preferred','Accessibility (WCAG) expertise','Accessibility (WCAG) expertise','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(279,5,'preferred','preferred','Have used or have experience within Maizzle','Maizzle','evidence',NULL,'skills',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(280,5,'preferred','preferred','AI/ML application interfaces','AI/ML application interfaces','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(281,5,'preferred','preferred','UI Design experience background','UI design experience','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(282,5,'preferred','preferred','UX Making sure the experience for the user is as slick as possible','UX focus on a slick user experience','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(283,5,'preferred','preferred','Able to rapidly prototype','Rapid prototyping','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(284,5,'preferred','preferred','Testing frameworks (Jest, Vitest, or Cypress)','Testing frameworks (Jest, Vitest or Cypress)','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(285,5,'responsibility','preferred','Migrate our legacy jQuery-based code to Vue 3 (a current modernisation project)','Migrate legacy jQuery code to Vue 3','evidence',NULL,'skills,experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(286,5,'responsibility','preferred','Build a component library, with references and documenting components for the team to use.','Build and document a component library','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(287,5,'responsibility','preferred','Champion best practices in component architecture, performance, and accessibility','Champion accessibility and performance best practices','evidence',NULL,'experience',0,NULL,NULL,NULL,NULL);
INSERT INTO "requirements" VALUES(288,5,'location','must_have','Location: Casablanca, Morocco','Role based in Casablanca','evidence',NULL,NULL,0,'Location kept must-have: the role is on site in Casablanca (checked by the reviewer, not Haiku).',NULL,NULL,NULL);
CREATE TABLE skill_keywords (
  skill_id INTEGER NOT NULL REFERENCES skills(id),
  keyword TEXT NOT NULL,
  lang TEXT NOT NULL CHECK (lang IN ('en', 'fr')),
  PRIMARY KEY (keyword, lang)
);
INSERT INTO "skill_keywords" VALUES(1,'WCAG','en');
INSERT INTO "skill_keywords" VALUES(14,'Web scraping','en');
INSERT INTO "skill_keywords" VALUES(23,'HTML5','en');
INSERT INTO "skill_keywords" VALUES(26,'ES6+','en');
INSERT INTO "skill_keywords" VALUES(30,'LLM Integration','en');
INSERT INTO "skill_keywords" VALUES(47,'SASS','en');
INSERT INTO "skill_keywords" VALUES(53,'Technical designs','en');
INSERT INTO "skill_keywords" VALUES(53,'technical design','en');
INSERT INTO "skill_keywords" VALUES(41,'Postgres','en');
INSERT INTO "skill_keywords" VALUES(34,'NextJS','en');
INSERT INTO "skill_keywords" VALUES(34,'Next js','en');
INSERT INTO "skill_keywords" VALUES(35,'NodeJS','en');
INSERT INTO "skill_keywords" VALUES(63,'Amazon Web Services','en');
INSERT INTO "skill_keywords" VALUES(64,'K8s','en');
INSERT INTO "skill_keywords" VALUES(6,'continuous integration','en');
INSERT INTO "skill_keywords" VALUES(6,'continuous delivery','en');
INSERT INTO "skill_keywords" VALUES(6,'continuous deployment','en');
INSERT INTO "skill_keywords" VALUES(65,'software as a service','en');
INSERT INTO "skill_keywords" VALUES(66,'API integrations','en');
INSERT INTO "skill_keywords" VALUES(66,'integrated APIs','en');
INSERT INTO "skill_keywords" VALUES(66,'integrating APIs','en');
INSERT INTO "skill_keywords" VALUES(66,'integrate APIs','en');
INSERT INTO "skill_keywords" VALUES(67,'API','en');
INSERT INTO "skill_keywords" VALUES(68,'automated tests','en');
INSERT INTO "skill_keywords" VALUES(68,'test automation','en');
INSERT INTO "skill_keywords" VALUES(68,'unit tests','en');
INSERT INTO "skill_keywords" VALUES(68,'integration tests','en');
INSERT INTO "skill_keywords" VALUES(68,'end-to-end tests','en');
INSERT INTO "skill_keywords" VALUES(69,'creator marketing','en');
INSERT INTO "skill_keywords" VALUES(69,'influencer marketing','en');
INSERT INTO "skill_keywords" VALUES(70,'prototype','en');
INSERT INTO "skill_keywords" VALUES(70,'prototyping','en');
INSERT INTO "skill_keywords" VALUES(71,'informatique','fr');
INSERT INTO "skill_keywords" VALUES(72,'agentic systems','en');
INSERT INTO "skill_keywords" VALUES(72,'agentic workflows','en');
INSERT INTO "skill_keywords" VALUES(73,'intelligence artificielle','fr');
INSERT INTO "skill_keywords" VALUES(73,'AI','en');
INSERT INTO "skill_keywords" VALUES(74,'bases de données','fr');
INSERT INTO "skill_keywords" VALUES(74,'database','en');
INSERT INTO "skill_keywords" VALUES(75,'tests','fr');
INSERT INTO "skill_keywords" VALUES(75,'tested','en');
INSERT INTO "skill_keywords" VALUES(76,'architectures distribuées','fr');
INSERT INTO "skill_keywords" VALUES(76,'distributed systems','en');
INSERT INTO "skill_keywords" VALUES(77,'sources de données','fr');
INSERT INTO "skill_keywords" VALUES(78,'architectural decisions','en');
INSERT INTO "skill_keywords" VALUES(79,'sécurité','fr');
INSERT INTO "skill_keywords" VALUES(9,'code review','en');
INSERT INTO "skill_keywords" VALUES(9,'code reviews','en');
INSERT INTO "skill_keywords" VALUES(82,'équipes techniques','fr');
INSERT INTO "skill_keywords" VALUES(82,'engineering teams','en');
INSERT INTO "skill_keywords" VALUES(84,'problématiques complexes','fr');
INSERT INTO "skill_keywords" VALUES(86,'orientation résultats','fr');
INSERT INTO "skill_keywords" VALUES(72,'IA agentique','fr');
INSERT INTO "skill_keywords" VALUES(78,'choix d''architecture','fr');
INSERT INTO "skill_keywords" VALUES(9,'revues de code','fr');
INSERT INTO "skill_keywords" VALUES(81,'tests techniques','fr');
INSERT INTO "skill_keywords" VALUES(85,'collaboration transverse','fr');
CREATE TABLE skill_layout (
  row INTEGER NOT NULL,
  position INTEGER NOT NULL,
  label_en TEXT NOT NULL,
  label_fr TEXT,
  PRIMARY KEY (row, position)
);
INSERT INTO "skill_layout" VALUES(1,1,'JavaScript',NULL);
INSERT INTO "skill_layout" VALUES(1,2,'Java',NULL);
INSERT INTO "skill_layout" VALUES(1,3,'Python',NULL);
INSERT INTO "skill_layout" VALUES(1,4,'PHP',NULL);
INSERT INTO "skill_layout" VALUES(2,1,'React / Next.js',NULL);
INSERT INTO "skill_layout" VALUES(2,2,'Angular',NULL);
INSERT INTO "skill_layout" VALUES(2,3,'Node.js / NestJS',NULL);
INSERT INTO "skill_layout" VALUES(2,4,'Spring Boot',NULL);
INSERT INTO "skill_layout" VALUES(3,1,'FastAPI',NULL);
INSERT INTO "skill_layout" VALUES(3,2,'WordPress',NULL);
INSERT INTO "skill_layout" VALUES(3,3,'Odoo',NULL);
INSERT INTO "skill_layout" VALUES(3,4,'PostgreSQL',NULL);
INSERT INTO "skill_layout" VALUES(4,1,'Data scraping','Scraping de données');
INSERT INTO "skill_layout" VALUES(4,2,'CI/CD',NULL);
INSERT INTO "skill_layout" VALUES(4,3,'Docker',NULL);
INSERT INTO "skill_layout" VALUES(4,4,'Testing Practices','Pratiques de test');
INSERT INTO "skill_layout" VALUES(5,1,'Figma',NULL);
INSERT INTO "skill_layout" VALUES(5,2,'Framer',NULL);
INSERT INTO "skill_layout" VALUES(5,3,'Interactive design','Design interactif');
INSERT INTO "skill_layout" VALUES(5,4,'Prototyping','Prototypage');
INSERT INTO "skill_layout" VALUES(6,1,'Claude Code & Codex',NULL);
INSERT INTO "skill_layout" VALUES(6,2,'MCP Integrations','Intégrations MCP');
INSERT INTO "skill_layout" VALUES(6,3,'LLM API Integration','Intégration d''API LLM');
INSERT INTO "skill_layout" VALUES(6,4,'AI Agent Workflows','Workflows d''agents IA');
CREATE TABLE skills (
  id INTEGER PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('technical', 'soft', 'language', 'location', 'design', 'ai')),
  name_en TEXT NOT NULL UNIQUE,
  name_fr TEXT,
  start_at TEXT,
  end_at TEXT
);
INSERT INTO "skills" VALUES(1,'technical','Accessibility',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(2,'ai','Agent Tooling',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(3,'ai','AI Agent Workflows','Workflows d''agents IA',NULL,NULL);
INSERT INTO "skills" VALUES(4,'technical','Angular',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(5,'technical','Blade',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(6,'technical','CI/CD',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(7,'ai','Claude',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(8,'ai','Claude Code',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(9,'technical','Code review','Revue de code',NULL,NULL);
INSERT INTO "skills" VALUES(10,'ai','Codex',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(11,'technical','CSS',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(12,'technical','Cypress',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(13,'technical','Data integration',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(14,'technical','Data scraping','Scraping de données',NULL,NULL);
INSERT INTO "skills" VALUES(15,'technical','Docker',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(16,'technical','Express',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(17,'technical','FastAPI',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(18,'design','Figma',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(19,'design','Framer',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(20,'technical','Git',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(21,'technical','Harness Eng',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(22,'technical','Hermes',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(23,'technical','HTML',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(24,'design','Interactive design','Design interactif',NULL,NULL);
INSERT INTO "skills" VALUES(25,'technical','Java',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(26,'technical','JavaScript',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(27,'technical','Jest',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(28,'technical','jQuery',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(29,'technical','Laravel',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(30,'ai','LLM API Integration','Intégration d''API LLM',NULL,NULL);
INSERT INTO "skills" VALUES(31,'ai','MCP Integrations','Intégrations MCP',NULL,NULL);
INSERT INTO "skills" VALUES(32,'technical','Microservices',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(33,'technical','NestJS',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(34,'technical','Next.js',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(35,'technical','Node.js',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(36,'technical','Nuxt.js',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(37,'technical','Obsidian',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(38,'technical','Odoo',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(39,'technical','PHP',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(40,'technical','Pinia',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(41,'technical','PostgreSQL',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(42,'design','Prototyping','Prototypage',NULL,NULL);
INSERT INTO "skills" VALUES(43,'technical','Python',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(44,'ai','RAG',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(45,'technical','React',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(46,'technical','REST APIs','API REST',NULL,NULL);
INSERT INTO "skills" VALUES(47,'technical','SCSS',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(48,'technical','SDKs',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(49,'technical','Sonar',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(50,'technical','Spring Boot',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(51,'technical','SQL',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(52,'technical','Symfony',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(53,'design','System design',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(54,'technical','Tailwind CSS',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(55,'technical','Testing Practices','Pratiques de test',NULL,NULL);
INSERT INTO "skills" VALUES(56,'technical','TypeScript',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(57,'design','UI Design',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(58,'technical','Vite',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(59,'technical','Vitest',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(60,'technical','Vue 3',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(61,'technical','Vue.js',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(62,'technical','WordPress',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(63,'technical','AWS',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(64,'technical','Kubernetes',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(65,'technical','SaaS',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(66,'technical','API integration',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(67,'technical','APIs',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(68,'technical','automated testing',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(69,'technical','creator-marketing',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(70,'technical','prototypes',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(71,'technical','Computer Science',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(72,'technical','agentic AI','IA agentique',NULL,NULL);
INSERT INTO "skills" VALUES(73,'technical','artificial intelligence',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(74,'technical','databases',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(75,'technical','testing',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(76,'technical','distributed architectures',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(77,'technical','data sources',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(78,'technical','architecture decisions','choix d''architecture',NULL,NULL);
INSERT INTO "skills" VALUES(79,'technical','security',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(81,'technical','technical testing','tests techniques',NULL,NULL);
INSERT INTO "skills" VALUES(82,'technical','technical teams',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(83,'technical','conception technique',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(84,'technical','complex problems',NULL,NULL,NULL);
INSERT INTO "skills" VALUES(85,'technical','cross-functional collaboration','collaboration transverse',NULL,NULL);
INSERT INTO "skills" VALUES(86,'technical','results-oriented',NULL,NULL,NULL);
COMMIT;
