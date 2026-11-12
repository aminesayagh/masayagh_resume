BEGIN TRANSACTION;
CREATE TABLE bloc_activities (
  id INTEGER PRIMARY KEY,
  experience_id INTEGER NOT NULL REFERENCES bloc_experiences(id),
  label TEXT NOT NULL,
  sort_order INTEGER NOT NULL,
  active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
);
INSERT INTO "bloc_activities" VALUES(1,1,'Tarifpublic.fr, provide technical consulting for',1,1);
INSERT INTO "bloc_activities" VALUES(2,1,'Develop AI agent workflows to',2,1);
INSERT INTO "bloc_activities" VALUES(3,2,'Developed product features for Hypeo,',1,1);
INSERT INTO "bloc_activities" VALUES(4,2,'Integrated an AI agent experience',2,1);
INSERT INTO "bloc_activities" VALUES(5,2,'Built and refined the front-end',3,1);
INSERT INTO "bloc_activities" VALUES(6,2,'Automated the manipulation and extraction',4,1);
INSERT INTO "bloc_activities" VALUES(7,2,'Took ownership of maintenance, deployment',5,1);
INSERT INTO "bloc_activities" VALUES(8,2,'Documented core business modules, missing',6,1);
INSERT INTO "bloc_activities" VALUES(9,2,'Developed an external data-metrics solution',7,1);
INSERT INTO "bloc_activities" VALUES(10,3,'Co-developed and rolled out a',1,1);
INSERT INTO "bloc_activities" VALUES(11,3,'Established a reusable prototyping approach',2,1);
INSERT INTO "bloc_activities" VALUES(12,3,'Tracked sprint KPIs in Odoo',3,1);
INSERT INTO "bloc_activities" VALUES(13,3,'Brought 02Book to production, an',4,1);
INSERT INTO "bloc_activities" VALUES(14,3,'Strengthened software design skills under',5,1);
INSERT INTO "bloc_activities" VALUES(15,4,'Designed and integrated product features',1,1);
INSERT INTO "bloc_activities" VALUES(16,4,'Designed UI flows and prototypes',2,1);
INSERT INTO "bloc_activities" VALUES(17,4,'Integrated data insights such as',3,1);
INSERT INTO "bloc_activities" VALUES(18,5,'Led web development of a',1,1);
INSERT INTO "bloc_activities" VALUES(19,5,'Implemented a Go API service',2,1);
INSERT INTO "bloc_activities" VALUES(20,5,'Developed the web experience of',3,1);
INSERT INTO "bloc_activities" VALUES(21,6,'Developed a responsive subscription website',1,1);
INSERT INTO "bloc_activities" VALUES(22,7,'Automated the delivery process for',1,1);
INSERT INTO "bloc_activities" VALUES(23,7,'Produced lead-capture websites that delivered',2,1);
CREATE TABLE bloc_certifications (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  issuer TEXT NOT NULL,
  link TEXT NOT NULL,
  date TEXT
);
INSERT INTO "bloc_certifications" VALUES(1,'Building with the Claude API','Anthropic','https://www.masayagh.com/badge/claude-api',NULL);
INSERT INTO "bloc_certifications" VALUES(2,'Model Context Protocol: Advanced Topics','Anthropic','https://www.masayagh.com/badge/mcp-advanced-topics',NULL);
INSERT INTO "bloc_certifications" VALUES(3,'Fundamentals of Agents','Hugging Face','https://www.masayagh.com/badge/fundamentals-of-agents',NULL);
CREATE TABLE bloc_contact (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  phone TEXT NOT NULL,
  website TEXT NOT NULL,
  github TEXT,
  linkedin TEXT,
  location_id INTEGER REFERENCES locations(id)
);
INSERT INTO "bloc_contact" VALUES(1,'Mohamed Amine Sayagh','mohamedamine@masayagh.com','(+212) 616-13 71 24','masayagh.com/hire','https://github.com/aminesayagh','https://linkedin.com/in/mohamedamine-sayagh',1);
CREATE TABLE bloc_descriptions (
  id INTEGER PRIMARY KEY,
  activity_id INTEGER NOT NULL REFERENCES bloc_activities(id),
  kind TEXT NOT NULL CHECK (kind IN ('description', 'bullet')),
  text TEXT NOT NULL,      -- json
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "bloc_descriptions" VALUES(1,1,'bullet','{"en": "Tarifpublic.fr, provide technical consulting for a French state-supported marketplace for public procurement, supporting standardized product pricing.", "fr": "Tarifpublic.fr : conseil technique pour une marketplace de la commande publique soutenue par l''État français, pour une tarification standardisée des produits."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(2,2,'bullet','{"en": "Develop AI agent workflows to automate business decisions for international agency engagements.", "fr": "Workflows d''agents IA pour automatiser les décisions métier des missions d''agences internationales."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(3,3,'description','{"en": "Developed product features for Hypeo, a MENA creator-marketing SaaS platform connecting influencers and media creators with businesses launching online content campaigns.", "fr": "Fonctionnalités produit pour Hypeo, plateforme SaaS de marketing d''influence (MENA) reliant influenceurs et créateurs aux entreprises qui lancent des campagnes de contenu en ligne."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(4,4,'bullet','{"en": "Integrated an AI agent experience that transforms open-ended client conversations into configured marketing campaigns, connected to the internal influencer database.", "fr": "Intégration d''une expérience d''agent IA qui transforme des conversations clients ouvertes en campagnes marketing configurées, reliée à la base interne d''influenceurs."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(5,5,'bullet','{"en": "Built and refined the front-end experience in close collaboration with a senior technical lead, continuously adapting workflows to backend integration and evolving business requirements.", "fr": "Conception et amélioration du front-end avec un lead technique senior, en adaptant les workflows à l''intégration back-end et à l''évolution des besoins métier."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(6,6,'bullet','{"en": "Automated the manipulation and extraction of influencer data from web-scraping outputs and database pipelines used across the platform.", "fr": "Automatisation de l''extraction et du traitement des données d''influenceurs issues du web scraping et des pipelines de données de la plateforme."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(7,7,'bullet','{"en": "Took ownership of maintenance, deployment support, access/IP handover, and bug-fix coordination during a technical leadership transition.", "fr": "Prise en charge de la maintenance, du support aux déploiements, de la passation des accès et de la PI, et de la coordination des correctifs lors d''une transition de direction technique."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(8,8,'bullet','{"en": "Documented core business modules, missing implementation areas, and architectural solutions to support future development planning.", "fr": "Documentation des modules métier clés, des zones non implémentées et des solutions d''architecture pour la planification des développements futurs."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(9,9,'bullet','{"en": "Developed an external data-metrics solution for creator audience and professional collaboration insights, later accepted and integrated into the company workflow.", "fr": "Solution externe de métriques sur l''audience des créateurs et leurs collaborations, ensuite adoptée et intégrée aux workflows de l''entreprise."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(10,10,'description','{"en": "Co-developed and rolled out a standardized software delivery process, aligning team workflows and contributing to lower shipping costs.", "fr": "Co-conception et déploiement d''un processus standardisé de livraison logicielle, alignant les workflows de l''équipe et réduisant les coûts de livraison."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(11,11,'bullet','{"en": "Established a reusable prototyping approach to validate business requirements across multiple use cases before development.", "fr": "Démarche de prototypage réutilisable pour valider les besoins métier sur plusieurs cas d''usage avant le développement."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(12,12,'bullet','{"en": "Tracked sprint KPIs in Odoo and surfaced bottlenecks to improve planning accuracy and throughput.", "fr": "Suivi des KPI de sprint dans Odoo et identification des blocages pour fiabiliser la planification et augmenter le débit."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(13,13,'bullet','{"en": "Brought 02Book to production, an AI-powered writing assistant for B2B writers, used by clients such as Orange and Le Matin.", "fr": "Mise en production de 02Book, assistant de rédaction IA pour rédacteurs B2B, utilisé par des clients comme Orange et Le Matin."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(14,14,'bullet','{"en": "Strengthened software design skills under continuous mentorship, working on client requirements and delivery constraints.", "fr": "Montée en compétences en conception logicielle sous mentorat continu, sur des besoins clients et des contraintes de livraison."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(15,15,'description','{"en": "Designed and integrated product features for Inflauditor, a business decision-making dashboard that helps brands analyze large-scale creator data for campaign planning. Delivered high-conversion lead-capture landing pages for Miratti (Morocco), French Dandy (Dubai), and Horde Studio (USA), supporting growth campaigns showcased at regional events (e.g., Forbes Middle East).", "fr": "Conception et intégration de fonctionnalités pour Inflauditor, tableau de bord d''aide à la décision qui permet aux marques d''analyser des données de créateurs à grande échelle. Landing pages de génération de leads à fort taux de conversion pour Miratti (Maroc), French Dandy (Dubaï) et Horde Studio (États-Unis), pour des campagnes présentées lors d''événements régionaux (ex. Forbes Middle East)."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(16,16,'bullet','{"en": "Designed UI flows and prototypes for Inflauditor to validate product direction and accelerate development decisions.", "fr": "Parcours UI et prototypes pour Inflauditor afin de valider l''orientation produit et d''accélérer les décisions de développement."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(17,17,'bullet','{"en": "Integrated data insights such as creator scoring, language detection, and sentiment indicators to support campaign planning.", "fr": "Intégration d''indicateurs (scoring des créateurs, détection de langue, analyse de sentiment) pour la planification des campagnes."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(18,18,'description','{"en": "Led web development of a CTF platform for security competitions, used in global events such as OWASP AppSec Days, BSides Singapore, and ISACA.", "fr": "Direction du développement web d''une plateforme CTF de compétitions de sécurité, utilisée lors d''événements comme OWASP AppSec Days, BSides Singapore et ISACA."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(19,19,'bullet','{"en": "Implemented a Go API service to orchestrate isolated application deployments, providing a secure training environment for participants.", "fr": "Service API en Go orchestrant des déploiements d''applications isolées, pour un environnement d''entraînement sécurisé."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(20,20,'bullet','{"en": "Developed the web experience of Warzone, a dashboard to track team progress, scoring and overall competition gamification.", "fr": "Expérience web de Warzone, tableau de bord de suivi de la progression des équipes, des scores et de la gamification."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(21,21,'description','{"en": "Developed a responsive subscription website for individual real estate investment plans.", "fr": "Développement d''un site d''abonnement responsive pour des plans d''investissement immobilier individuels."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(22,22,'bullet','{"en": "Automated the delivery process for new websites by reusing proven experience patterns, helping shorten release cycles.", "fr": "Automatisation de la livraison de nouveaux sites par la réutilisation de modèles éprouvés, réduisant les cycles de mise en production."}','approved','2026-11-12 18:16:45');
INSERT INTO "bloc_descriptions" VALUES(23,23,'bullet','{"en": "Produced lead-capture websites that delivered strong conversion performance for client campaigns.", "fr": "Sites de génération de leads à forte conversion pour les campagnes clients."}','approved','2026-11-12 18:16:45');
CREATE TABLE bloc_education (
  id INTEGER PRIMARY KEY,
  degree TEXT NOT NULL,       -- json
  institution TEXT NOT NULL,  -- json
  start_at TEXT NOT NULL,
  end_at TEXT NOT NULL
);
INSERT INTO "bloc_education" VALUES(1,'{"en": "Master''s in Big Data & Cloud Computing", "fr": "Master en Big Data & Cloud Computing"}','{"en": "University of Hassan 2, Casablanca", "fr": "Université Hassan II, Casablanca"}','2023','2025');
INSERT INTO "bloc_education" VALUES(2,'{"en": "Bachelor''s in Computer Science", "fr": "Licence en informatique"}','{"en": "University of Hassan 2, Casablanca", "fr": "Université Hassan II, Casablanca"}','2020','2023');
CREATE TABLE bloc_experiences (
  id INTEGER PRIMARY KEY,
  contract_id INTEGER NOT NULL REFERENCES contracts(id),
  role TEXT NOT NULL,      -- json
  location TEXT            -- json ("Morocco" / "Maroc"); free text, not linked to locations (countries and cities)
);
INSERT INTO "bloc_experiences" VALUES(1,1,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "France"}');
INSERT INTO "bloc_experiences" VALUES(2,2,'{"en": "Software Developer", "fr": "Développeur logiciel"}',NULL);
INSERT INTO "bloc_experiences" VALUES(3,3,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "Morocco", "fr": "Maroc"}');
INSERT INTO "bloc_experiences" VALUES(4,4,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "Morocco", "fr": "Maroc"}');
INSERT INTO "bloc_experiences" VALUES(5,5,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "Singapore", "fr": "Singapour"}');
INSERT INTO "bloc_experiences" VALUES(6,6,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "France"}');
INSERT INTO "bloc_experiences" VALUES(7,7,'{"en": "Full Stack Developer", "fr": "Développeur Full Stack"}','{"en": "London", "fr": "Londres"}');
INSERT INTO "bloc_experiences" VALUES(8,8,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "France"}');
INSERT INTO "bloc_experiences" VALUES(9,9,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "London", "fr": "Londres"}');
INSERT INTO "bloc_experiences" VALUES(10,10,'{"en": "Software Developer", "fr": "Développeur logiciel"}','{"en": "Morocco", "fr": "Maroc"}');
INSERT INTO "bloc_experiences" VALUES(11,11,'{"en": "Web Designer", "fr": "Web designer"}','{"en": "Morocco", "fr": "Maroc"}');
CREATE TABLE bloc_languages (
  id INTEGER PRIMARY KEY,
  sort_order INTEGER NOT NULL,
  name TEXT NOT NULL,      -- json
  level TEXT NOT NULL      -- json
);
INSERT INTO "bloc_languages" VALUES(1,1,'{"en": "Arabic", "fr": "Arabe"}','{"en": "Native", "fr": "Langue maternelle"}');
INSERT INTO "bloc_languages" VALUES(2,2,'{"en": "French", "fr": "Français"}','{"en": "Professional", "fr": "Professionnel"}');
INSERT INTO "bloc_languages" VALUES(3,3,'{"en": "English", "fr": "Anglais"}','{"en": "Professional", "fr": "Professionnel"}');
CREATE TABLE bloc_profile (
  id INTEGER PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  text TEXT NOT NULL       -- json
);
INSERT INTO "bloc_profile" VALUES(1,'role','{"en": "Software Engineer", "fr": "Ingénieur logiciel"}');
INSERT INTO "bloc_profile" VALUES(2,'summary','{"en": "Software developer building product experiences that simplify complex processes. Combining engineering, visual design, business understanding, and AI-assisted development to turn inefficient workflows into practical tools that help teams get more done. Looking to join a team that ships products at scale.", "fr": "Développeur logiciel qui conçoit des expériences produit simplifiant des processus complexes. J''allie ingénierie, design visuel, sens métier et développement assisté par l''IA pour transformer des workflows inefficaces en outils concrets qui rendent les équipes plus efficaces. Je souhaite rejoindre une équipe qui livre des produits à grande échelle."}');
CREATE TABLE bloc_projects (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  tech TEXT NOT NULL,      -- json
  link TEXT NOT NULL,
  duration TEXT NOT NULL   -- json
);
INSERT INTO "bloc_projects" VALUES(1,'OrbitRows CLI','{"en": "Python · CLI · AI Agent · SQLite · SQL · JEV · GLiNER2", "fr": "Python · CLI · Agent IA · SQLite · SQL · JEV · GLiNER2"}','https://www.masayagh.com/work/orbitrows/','{"en": "21 working days", "fr": "21 jours ouvrés"}');
INSERT INTO "bloc_projects" VALUES(2,'LingoWP','{"en": "WordPress · React · Python · FastAPI · PostgreSQL · FreeBSD"}','https://www.masayagh.com/work/lingowp/','{"en": "43 working days", "fr": "43 jours ouvrés"}');
CREATE TABLE bloc_skill_layout (
  row INTEGER NOT NULL,
  position INTEGER NOT NULL,
  label TEXT NOT NULL,     -- json
  PRIMARY KEY (row, position)
);
INSERT INTO "bloc_skill_layout" VALUES(1,1,'{"en": "JavaScript"}');
INSERT INTO "bloc_skill_layout" VALUES(1,2,'{"en": "Java"}');
INSERT INTO "bloc_skill_layout" VALUES(1,3,'{"en": "Python"}');
INSERT INTO "bloc_skill_layout" VALUES(1,4,'{"en": "PHP"}');
INSERT INTO "bloc_skill_layout" VALUES(2,1,'{"en": "React / Next.js"}');
INSERT INTO "bloc_skill_layout" VALUES(2,2,'{"en": "Angular"}');
INSERT INTO "bloc_skill_layout" VALUES(2,3,'{"en": "Node.js / NestJS"}');
INSERT INTO "bloc_skill_layout" VALUES(2,4,'{"en": "Spring Boot"}');
INSERT INTO "bloc_skill_layout" VALUES(3,1,'{"en": "FastAPI"}');
INSERT INTO "bloc_skill_layout" VALUES(3,2,'{"en": "WordPress"}');
INSERT INTO "bloc_skill_layout" VALUES(3,3,'{"en": "Odoo"}');
INSERT INTO "bloc_skill_layout" VALUES(3,4,'{"en": "PostgreSQL"}');
INSERT INTO "bloc_skill_layout" VALUES(4,1,'{"en": "Data scraping", "fr": "Scraping de données"}');
INSERT INTO "bloc_skill_layout" VALUES(4,2,'{"en": "CI/CD"}');
INSERT INTO "bloc_skill_layout" VALUES(4,3,'{"en": "Docker"}');
INSERT INTO "bloc_skill_layout" VALUES(4,4,'{"en": "Testing Practices", "fr": "Pratiques de test"}');
INSERT INTO "bloc_skill_layout" VALUES(5,1,'{"en": "Figma"}');
INSERT INTO "bloc_skill_layout" VALUES(5,2,'{"en": "Framer"}');
INSERT INTO "bloc_skill_layout" VALUES(5,3,'{"en": "Interactive design", "fr": "Design interactif"}');
INSERT INTO "bloc_skill_layout" VALUES(5,4,'{"en": "Prototyping", "fr": "Prototypage"}');
INSERT INTO "bloc_skill_layout" VALUES(6,1,'{"en": "Claude Code & Codex"}');
INSERT INTO "bloc_skill_layout" VALUES(6,2,'{"en": "MCP Integrations", "fr": "Intégrations MCP"}');
INSERT INTO "bloc_skill_layout" VALUES(6,3,'{"en": "LLM API Integration", "fr": "Intégration d''API LLM"}');
INSERT INTO "bloc_skill_layout" VALUES(6,4,'{"en": "AI Agent Workflows", "fr": "Workflows d''agents IA"}');
CREATE TABLE companies (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL       -- json; employers, self-employment and offer companies alike
);
INSERT INTO "companies" VALUES(1,'{"en": "Technical Consultant", "fr": "Consultant technique"}');
INSERT INTO "companies" VALUES(2,'{"en": "Phoenix AI USA Inc."}');
INSERT INTO "companies" VALUES(3,'{"en": "Cogy Tech"}');
INSERT INTO "companies" VALUES(4,'{"en": "Rich Media"}');
INSERT INTO "companies" VALUES(5,'{"en": "Cyber Cohesion"}');
INSERT INTO "companies" VALUES(6,'{"en": "Sodiadd"}');
INSERT INTO "companies" VALUES(7,'{"en": "Jonas Agency"}');
INSERT INTO "companies" VALUES(8,'{"en": "Happy Water NFT"}');
INSERT INTO "companies" VALUES(9,'{"en": "Lavish Trading"}');
INSERT INTO "companies" VALUES(10,'{"en": "MySchool"}');
INSERT INTO "companies" VALUES(11,'{"en": "Freelance"}');
CREATE TABLE compositions (
  id INTEGER PRIMARY KEY,
  offer_id INTEGER REFERENCES offers(id),   -- optional: a resume can be composed without an offer
  folder TEXT NOT NULL UNIQUE,              -- jobs/<slug>-vN: where its files are
  pdf_name TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at TEXT NOT NULL DEFAULT (datetime('now')),
  sent_at TEXT,
  template_sha TEXT
);
CREATE TABLE contracts (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  type TEXT NOT NULL CHECK (type IN ('job', 'freelance')),
  start_at TEXT NOT NULL,
  end_at TEXT
);
INSERT INTO "contracts" VALUES(1,1,'job','2026-09',NULL);
INSERT INTO "contracts" VALUES(2,2,'job','2025-07','2026-09');
INSERT INTO "contracts" VALUES(3,3,'job','2025-02','2025-06');
INSERT INTO "contracts" VALUES(4,4,'job','2024-08','2025-01');
INSERT INTO "contracts" VALUES(5,5,'job','2023-08','2024-07');
INSERT INTO "contracts" VALUES(6,6,'job','2023-05','2023-07');
INSERT INTO "contracts" VALUES(7,7,'job','2022-10','2023-04');
INSERT INTO "contracts" VALUES(8,8,'job','2022-07','2022-09');
INSERT INTO "contracts" VALUES(9,9,'job','2021-08','2022-06');
INSERT INTO "contracts" VALUES(10,10,'job','2021-01','2021-06');
INSERT INTO "contracts" VALUES(11,11,'freelance','2016','2020');
CREATE TABLE cover_paragraph_experiences (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id) ON DELETE CASCADE,
  experience_id INTEGER NOT NULL REFERENCES bloc_experiences(id) ON DELETE CASCADE,
  PRIMARY KEY (paragraph_id, experience_id)
);
CREATE TABLE cover_paragraph_skills (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (paragraph_id, skill_id)
);
CREATE TABLE cover_paragraphs (
  id INTEGER PRIMARY KEY,
  part TEXT NOT NULL CHECK (part IN ('opening', 'example', 'support', 'close')),
  text TEXT NOT NULL,      -- json
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE description_skills (
  description_id INTEGER NOT NULL REFERENCES bloc_descriptions(id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (description_id, skill_id)
);
INSERT INTO "description_skills" VALUES(2,26);
INSERT INTO "description_skills" VALUES(11,22);
INSERT INTO "description_skills" VALUES(12,13);
CREATE TABLE interview_notes (
  requirement_id INTEGER PRIMARY KEY REFERENCES requirements(id) ON DELETE CASCADE,
  note TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE locations (
  id INTEGER PRIMARY KEY,
  city TEXT NOT NULL,      -- json {"en", "fr"}
  country TEXT NOT NULL    -- json {"en", "fr"}
);
INSERT INTO "locations" VALUES(1,'{"en": "Casablanca"}','{"en": "Morocco", "fr": "Maroc"}');
CREATE TABLE offer_lines (
  composition_id INTEGER NOT NULL REFERENCES compositions(id) ON DELETE CASCADE,
  position INTEGER NOT NULL,
  description_id INTEGER NOT NULL REFERENCES bloc_descriptions(id),
  PRIMARY KEY (composition_id, position)
);
CREATE TABLE offers (
  id INTEGER PRIMARY KEY,
  company_id INTEGER NOT NULL REFERENCES companies(id),
  title TEXT NOT NULL,
  link TEXT,
  posting TEXT NOT NULL,
  language TEXT NOT NULL,
  english_mentioned INTEGER NOT NULL DEFAULT 0 CHECK (english_mentioned IN (0, 1)),
  location_id INTEGER REFERENCES locations(id),
  created_at TEXT NOT NULL DEFAULT (date('now')),
  resume_url TEXT,         -- one public link per offer; the cover letter is inside the same PDF
  skipped_terms TEXT       -- json {term: reason}; open point: a table or nothing
);
CREATE TABLE requirements (
  id INTEGER PRIMARY KEY,
  offer_id INTEGER NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
  keyword_id INTEGER NOT NULL REFERENCES skill_keywords(id),
  priority INTEGER NOT NULL CHECK (priority BETWEEN 0 AND 100),
  min_years REAL CHECK (min_years IS NULL OR min_years > 0),
  UNIQUE (offer_id, keyword_id)
);
CREATE TABLE skill_keywords (
  id INTEGER PRIMARY KEY,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  keyword TEXT NOT NULL,   -- lowercase; a skill's own name is one of its keywords
  lang TEXT NOT NULL CHECK (lang IN ('en', 'fr')),
  UNIQUE (keyword, lang)
);
INSERT INTO "skill_keywords" VALUES(1,1,'javascript','en');
INSERT INTO "skill_keywords" VALUES(2,2,'java','en');
INSERT INTO "skill_keywords" VALUES(3,3,'python','en');
INSERT INTO "skill_keywords" VALUES(4,4,'php','en');
INSERT INTO "skill_keywords" VALUES(5,5,'react','en');
INSERT INTO "skill_keywords" VALUES(6,6,'next.js','en');
INSERT INTO "skill_keywords" VALUES(7,7,'angular','en');
INSERT INTO "skill_keywords" VALUES(8,8,'node.js','en');
INSERT INTO "skill_keywords" VALUES(9,9,'nestjs','en');
INSERT INTO "skill_keywords" VALUES(10,10,'spring boot','en');
INSERT INTO "skill_keywords" VALUES(11,11,'fastapi','en');
INSERT INTO "skill_keywords" VALUES(12,12,'wordpress','en');
INSERT INTO "skill_keywords" VALUES(13,13,'odoo','en');
INSERT INTO "skill_keywords" VALUES(14,14,'postgresql','en');
INSERT INTO "skill_keywords" VALUES(15,15,'data scraping','en');
INSERT INTO "skill_keywords" VALUES(16,16,'ci/cd','en');
INSERT INTO "skill_keywords" VALUES(17,17,'docker','en');
INSERT INTO "skill_keywords" VALUES(18,18,'testing practices','en');
INSERT INTO "skill_keywords" VALUES(19,19,'figma','en');
INSERT INTO "skill_keywords" VALUES(20,20,'framer','en');
INSERT INTO "skill_keywords" VALUES(21,21,'interactive design','en');
INSERT INTO "skill_keywords" VALUES(22,22,'prototyping','en');
INSERT INTO "skill_keywords" VALUES(23,23,'claude code & codex','en');
INSERT INTO "skill_keywords" VALUES(24,24,'mcp integrations','en');
INSERT INTO "skill_keywords" VALUES(25,25,'llm api integration','en');
INSERT INTO "skill_keywords" VALUES(26,26,'ai agent workflows','en');
CREATE TABLE skills (
  id INTEGER PRIMARY KEY,
  type TEXT CHECK (type IN ('technical', 'design', 'ai', 'soft', 'language', 'location', 'education')),  -- NULL = not typed yet
  name TEXT NOT NULL,      -- json, lowercase
  start_at TEXT,
  end_at TEXT,
  confirmed INTEGER NOT NULL DEFAULT 1 CHECK (confirmed IN (0, 1))  -- 0 = created from a posting, to review or merge
);
INSERT INTO "skills" VALUES(1,NULL,'{"en": "javascript"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(2,NULL,'{"en": "java"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(3,NULL,'{"en": "python"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(4,NULL,'{"en": "php"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(5,NULL,'{"en": "react"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(6,NULL,'{"en": "next.js"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(7,NULL,'{"en": "angular"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(8,NULL,'{"en": "node.js"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(9,NULL,'{"en": "nestjs"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(10,NULL,'{"en": "spring boot"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(11,NULL,'{"en": "fastapi"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(12,NULL,'{"en": "wordpress"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(13,NULL,'{"en": "odoo"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(14,NULL,'{"en": "postgresql"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(15,NULL,'{"en": "data scraping"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(16,NULL,'{"en": "ci/cd"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(17,NULL,'{"en": "docker"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(18,NULL,'{"en": "testing practices"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(19,NULL,'{"en": "figma"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(20,NULL,'{"en": "framer"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(21,NULL,'{"en": "interactive design"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(22,NULL,'{"en": "prototyping"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(23,NULL,'{"en": "claude code & codex"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(24,NULL,'{"en": "mcp integrations"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(25,NULL,'{"en": "llm api integration"}',NULL,NULL,1);
INSERT INTO "skills" VALUES(26,NULL,'{"en": "ai agent workflows"}',NULL,NULL,1);
COMMIT;
