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
, score TEXT);
INSERT INTO "bloc_descriptions" VALUES(1,1,'bullet','{"en": "Tarifpublic.fr, provide technical consulting for a French state-supported marketplace for public procurement, supporting standardized product pricing.", "fr": "Tarifpublic.fr : conseil technique pour une marketplace de la commande publique soutenue par l''État français, pour une tarification standardisée des produits."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 1, "contribution": 1, "clarity": 1}, "supporting_phrases": {"result": "supporting standardized product pricing", "evidence": "a French state-supported marketplace for public procurement", "contribution": "provide technical consulting", "clarity": "Tarifpublic.fr, provide technical consulting"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the standardized pricing changed for the marketplace or its users.", "Add a verified scope or adoption detail that shows the reach of the pricing work.", "Name the specific technical deliverable the candidate built or changed.", "Rewrite as a full sentence with a clear subject and verb, since the line opens with a site name and a fragment.", "Add evidence that the pricing standardization was delivered, since none is given."], "total": 4, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "9fefaad92fb675fa", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(2,2,'bullet','{"en": "Develop AI agent workflows to automate business decisions for international agency engagements.", "fr": "Workflows d''agents IA pour automatiser les décisions métier des missions d''agences internationales."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "to automate business decisions", "evidence": null, "contribution": "Develop AI agent workflows", "clarity": "Develop AI agent workflows to automate business decisions"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the automated workflows improved or made possible for the agency engagements.", "Add a verified metric, adoption count, or concrete scope for the workflows.", "Add evidence that the workflows automated decisions, such as the decisions covered or the engagements that used them."], "total": 5, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "c03e7a83131bd14b", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(3,3,'description','{"en": "Developed product features for Hypeo, a MENA creator-marketing SaaS platform connecting influencers and media creators with businesses launching online content campaigns.", "fr": "Fonctionnalités produit pour Hypeo, plateforme SaaS de marketing d''influence (MENA) reliant influenceurs et créateurs aux entreprises qui lancent des campagnes de contenu en ligne."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 1, "contribution": 1, "clarity": 2}, "supporting_phrases": {"result": "Developed product features for Hypeo", "evidence": "a MENA creator-marketing SaaS platform", "contribution": "Developed product features", "clarity": "Developed product features for Hypeo"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the features enabled for users or the business.", "Add a verified scope, rollout, or adoption detail for the features.", "Name the specific features the candidate built or changed.", "Add evidence tied to the features delivered, such as rollout or usage scope."], "total": 5, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "77ef26f43ccc7913", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(4,4,'bullet','{"en": "Integrated an AI agent experience that transforms open-ended client conversations into configured marketing campaigns, connected to the internal influencer database.", "fr": "Intégration d''une expérience d''agent IA qui transforme des conversations clients ouvertes en campagnes marketing configurées, reliée à la base interne d''influenceurs."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 1, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "transforms open-ended client conversations into configured marketing campaigns", "evidence": "connected to the internal influencer database", "contribution": "Integrated an AI agent experience", "clarity": "Integrated an AI agent experience that transforms open-ended client conversations"}, "evidence_type": "scope", "claim_evidence_match": "partial", "attribution": "individual", "revision_requests": ["Add a verified usage, adoption, or rollout detail for the agent experience.", "Add evidence that the generated campaigns were used or delivered, such as counts or rollout scope."], "total": 7, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "f4945a132cc42859", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(5,5,'bullet','{"en": "Built and refined the front-end experience in close collaboration with a senior technical lead, continuously adapting workflows to backend integration and evolving business requirements.", "fr": "Conception et amélioration du front-end avec un lead technique senior, en adaptant les workflows à l''intégration back-end et à l''évolution des besoins métier."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "Built and refined the front-end experience", "evidence": null, "contribution": "Built and refined the front-end experience", "clarity": "Built and refined the front-end experience"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the refined front-end enabled or improved for users or the business.", "Add a verified detail such as a release, user group, or scope for the front-end work.", "Add evidence that the front-end work was released or adopted."], "total": 5, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "d0916aa709f867c3", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(6,6,'bullet','{"en": "Automated the manipulation and extraction of influencer data from web-scraping outputs and database pipelines used across the platform.", "fr": "Automatisation de l''extraction et du traitement des données d''influenceurs issues du web scraping et des pipelines de données de la plateforme."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 1, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "Automated the manipulation and extraction of influencer data", "evidence": "used across the platform", "contribution": "Automated the manipulation and extraction of influencer data", "clarity": "Automated the manipulation and extraction of influencer data"}, "evidence_type": "scope", "claim_evidence_match": "supports", "attribution": "individual", "revision_requests": ["State what the automation improved, such as time saved or data quality, only if verified.", "Add a verified metric or scope detail, such as the volume of data processed."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "c759b8861e9786ea", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(7,7,'bullet','{"en": "Took ownership of maintenance, deployment support, access/IP handover, and bug-fix coordination during a technical leadership transition.", "fr": "Prise en charge de la maintenance, du support aux déploiements, de la passation des accès et de la PI, et de la coordination des correctifs lors d''une transition de direction technique."}','approved','2026-11-12 18:16:45','{"scores": {"result": 0, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": null, "evidence": null, "contribution": "Took ownership of maintenance, deployment support, access/IP handover, and bug-fix coordination", "clarity": "Took ownership of maintenance, deployment support, access/IP handover, and bug-fix coordination during a technical leadership transition"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the handover achieved, such as continuity of the platform, only if verified.", "Add a verified detail that shows the scope or outcome of the handover, such as timeframe or what kept running.", "Add evidence of the handover outcome, since the line lists duties only."], "total": 4, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "231996a6a600c05a", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(8,8,'bullet','{"en": "Documented core business modules, missing implementation areas, and architectural solutions to support future development planning.", "fr": "Documentation des modules métier clés, des zones non implémentées et des solutions d''architecture pour la planification des développements futurs."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "to support future development planning", "evidence": null, "contribution": "Documented core business modules, missing implementation areas, and architectural solutions", "clarity": "Documented core business modules, missing implementation areas, and architectural solutions"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the documentation enabled, such as faster planning, only if verified.", "Add a verified scope detail, such as which modules or areas were documented.", "Add evidence that the documentation was used for planning, or present it only as documentation produced."], "total": 5, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "6c5238a69a77e002", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(9,9,'bullet','{"en": "Developed an external data-metrics solution for creator audience and professional collaboration insights, later accepted and integrated into the company workflow.", "fr": "Solution externe de métriques sur l''audience des créateurs et leurs collaborations, ensuite adoptée et intégrée aux workflows de l''entreprise."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 1, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "later accepted and integrated into the company workflow", "evidence": "later accepted and integrated into the company workflow", "contribution": "Developed an external data-metrics solution", "clarity": "Developed an external data-metrics solution for creator audience and professional collaboration insights"}, "evidence_type": "adoption", "claim_evidence_match": "partial", "attribution": "individual", "revision_requests": ["State what the metrics solution enabled or improved for the company or its users.", "Add an adoption detail, such as the number of teams or users using it.", "Add the scope of the integration, such as which workflows or teams it reached."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "927556bb9264052b", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(10,10,'description','{"en": "Co-developed and rolled out a standardized software delivery process, aligning team workflows and contributing to lower shipping costs.", "fr": "Co-conception et déploiement d''un processus standardisé de livraison logicielle, alignant les workflows de l''équipe et réduisant les coûts de livraison."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 1, "contribution": 1, "clarity": 2}, "supporting_phrases": {"result": "contributing to lower shipping costs", "evidence": "rolled out a standardized software delivery process", "contribution": "Co-developed and rolled out", "clarity": "Co-developed and rolled out a standardized software delivery process, aligning team workflows"}, "evidence_type": "delivery", "claim_evidence_match": "missing", "attribution": "unclear", "revision_requests": ["Add a verified scope or adoption detail for the rollout, such as the teams covered.", "Name the candidate''s own part in the process, not only the shared co-development.", "Add evidence of the shipping-cost change, or remove the cost claim."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "9f025294c6fa4920", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(11,11,'bullet','{"en": "Established a reusable prototyping approach to validate business requirements across multiple use cases before development.", "fr": "Démarche de prototypage réutilisable pour valider les besoins métier sur plusieurs cas d''usage avant le développement."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 1, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "to validate business requirements across multiple use cases before development", "evidence": "across multiple use cases", "contribution": "Established a reusable prototyping approach", "clarity": "Established a reusable prototyping approach to validate business requirements"}, "evidence_type": "scope", "claim_evidence_match": "partial", "attribution": "individual", "revision_requests": ["Add a concrete scope detail, such as how many use cases the approach covered.", "Name the verified use cases in which the approach validated requirements."], "total": 7, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "9ec994ecf875a6d8", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(12,12,'bullet','{"en": "Tracked sprint KPIs in Odoo and surfaced bottlenecks to improve planning accuracy and throughput.", "fr": "Suivi des KPI de sprint dans Odoo et identification des blocages pour fiabiliser la planification et augmenter le débit."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 1, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "to improve planning accuracy and throughput", "evidence": "Tracked sprint KPIs in Odoo", "contribution": "Tracked sprint KPIs in Odoo and surfaced bottlenecks", "clarity": "Tracked sprint KPIs in Odoo and surfaced bottlenecks to improve planning accuracy and throughput"}, "evidence_type": "scope", "claim_evidence_match": "partial", "attribution": "individual", "revision_requests": ["Add a verified measured change in planning accuracy or throughput, only if one exists.", "Add evidence of the planning or throughput change, or reword the claim to describe the tracking done."], "total": 7, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "2b4c8bf48fc30a6a", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(13,13,'bullet','{"en": "Brought 02Book to production, an AI-powered writing assistant for B2B writers, used by clients such as Orange and Le Matin.", "fr": "Mise en production de 02Book, assistant de rédaction IA pour rédacteurs B2B, utilisé par des clients comme Orange et Le Matin."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 2, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "Brought 02Book to production", "evidence": "used by clients such as Orange and Le Matin", "contribution": "Brought 02Book to production", "clarity": "Brought 02Book to production, an AI-powered writing assistant for B2B writers"}, "evidence_type": "adoption", "claim_evidence_match": "supports", "attribution": "individual", "revision_requests": ["State what the product enabled or changed for its clients or users."], "total": 7, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "10b04dc35cdb1ca4", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(14,14,'bullet','{"en": "Strengthened software design skills under continuous mentorship, working on client requirements and delivery constraints.", "fr": "Montée en compétences en conception logicielle sous mentorat continu, sur des besoins clients et des contraintes de livraison."}','approved','2026-11-12 18:16:45','{"scores": {"result": 0, "evidence": 0, "contribution": 1, "clarity": 2}, "supporting_phrases": {"result": null, "evidence": null, "contribution": "working on client requirements and delivery constraints", "clarity": "Strengthened software design skills under continuous mentorship"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["Replace the skill-growth wording with a concrete outcome of the client work, only if verified.", "Add an observable detail of the client work delivered, only if verified.", "Name the specific design work the candidate built or changed.", "Add an observable outcome of the mentored work, or drop the skill-growth claim."], "total": 3, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "c4f917338ade31d7", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(15,15,'description','{"en": "Designed and integrated product features for Inflauditor, a business decision-making dashboard that helps brands analyze large-scale creator data for campaign planning. Delivered high-conversion lead-capture landing pages for Miratti (Morocco), French Dandy (Dubai), and Horde Studio (USA), supporting growth campaigns showcased at regional events (e.g., Forbes Middle East).", "fr": "Conception et intégration de fonctionnalités pour Inflauditor, tableau de bord d''aide à la décision qui permet aux marques d''analyser des données de créateurs à grande échelle. Landing pages de génération de leads à fort taux de conversion pour Miratti (Maroc), French Dandy (Dubaï) et Horde Studio (États-Unis), pour des campagnes présentées lors d''événements régionaux (ex. Forbes Middle East)."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 2, "contribution": 2, "clarity": 1}, "supporting_phrases": {"result": "helps brands analyze large-scale creator data for campaign planning", "evidence": "Delivered high-conversion lead-capture landing pages for Miratti (Morocco), French Dandy (Dubai), and Horde Studio (USA)", "contribution": "Designed and integrated product features for Inflauditor", "clarity": "Designed and integrated product features for Inflauditor, a business decision-making dashboard"}, "evidence_type": "scope", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["Split the dashboard work and the landing-page work into separate lines, so one main point reads first.", "Add a measured conversion figure for the landing pages, or remove the high-conversion claim."], "total": 7, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "abdff4613732aa12", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(16,16,'bullet','{"en": "Designed UI flows and prototypes for Inflauditor to validate product direction and accelerate development decisions.", "fr": "Parcours UI et prototypes pour Inflauditor afin de valider l''orientation produit et d''accélérer les décisions de développement."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "to validate product direction and accelerate development decisions", "evidence": null, "contribution": "Designed UI flows and prototypes for Inflauditor", "clarity": "Designed UI flows and prototypes for Inflauditor to validate product direction"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["Add a concrete detail of the prototyping result, such as the decisions it informed, only if verified.", "Add evidence that the prototypes shortened development or informed decisions, or remove the acceleration claim."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "28c1293f3e21fce1", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(17,17,'bullet','{"en": "Integrated data insights such as creator scoring, language detection, and sentiment indicators to support campaign planning.", "fr": "Intégration d''indicateurs (scoring des créateurs, détection de langue, analyse de sentiment) pour la planification des campagnes."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 1, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "to support campaign planning", "evidence": "creator scoring, language detection, and sentiment indicators", "contribution": "Integrated data insights", "clarity": "Integrated data insights such as creator scoring, language detection, and sentiment indicators"}, "evidence_type": "scope", "claim_evidence_match": "partial", "attribution": "individual", "revision_requests": ["State what campaign planning gained from the insights, only if verified.", "Add a verified scope or adoption detail, such as which clients or campaigns used the insights.", "Add evidence that the insights were used in campaign planning."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "5008b2c9d894d4ca", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(18,18,'description','{"en": "Led web development of a CTF platform for security competitions, used in global events such as OWASP AppSec Days, BSides Singapore, and ISACA.", "fr": "Direction du développement web d''une plateforme CTF de compétitions de sécurité, utilisée lors d''événements comme OWASP AppSec Days, BSides Singapore et ISACA."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 2, "contribution": 2, "clarity": 1}, "supporting_phrases": {"result": "Led web development of a CTF platform for security competitions", "evidence": "used in global events such as OWASP AppSec Days, BSides Singapore, and ISACA", "contribution": "Led web development of a CTF platform", "clarity": "Led web development of a CTF platform for security competitions"}, "evidence_type": "adoption", "claim_evidence_match": "supports", "attribution": "individual", "revision_requests": ["State what the platform enabled for participants or organizers, only if verified.", "Describe what a CTF platform does in plain words, since the term is not explained."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "28c345bef87467a7", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(19,19,'bullet','{"en": "Implemented a Go API service to orchestrate isolated application deployments, providing a secure training environment for participants.", "fr": "Service API en Go orchestrant des déploiements d''applications isolées, pour un environnement d''entraînement sécurisé."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 1, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "providing a secure training environment for participants", "evidence": "to orchestrate isolated application deployments", "contribution": "Implemented a Go API service", "clarity": "Implemented a Go API service to orchestrate isolated application deployments"}, "evidence_type": "scope", "claim_evidence_match": "partial", "attribution": "individual", "revision_requests": ["Add a verified scope detail, such as the number of participants or environments supported.", "Add evidence for the security claim, such as how isolation was achieved, or soften the word secure."], "total": 7, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "55a556dd9e0c8c2b", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(20,20,'bullet','{"en": "Developed the web experience of Warzone, a dashboard to track team progress, scoring and overall competition gamification.", "fr": "Expérience web de Warzone, tableau de bord de suivi de la progression des équipes, des scores et de la gamification."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "a dashboard to track team progress, scoring and overall competition gamification", "evidence": null, "contribution": "Developed the web experience of Warzone", "clarity": "Developed the web experience of Warzone, a dashboard to track team progress"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the dashboard enabled for teams or participants, only if verified.", "Add a verified scope or adoption detail, such as the number of teams or users.", "Add evidence the dashboard was used, such as usage or rollout scope."], "total": 5, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "11640f11096dee3d", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(21,21,'description','{"en": "Developed a responsive subscription website for individual real estate investment plans.", "fr": "Développement d''un site d''abonnement responsive pour des plans d''investissement immobilier individuels."}','approved','2026-11-12 18:16:45','{"scores": {"result": 1, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "Developed a responsive subscription website", "evidence": null, "contribution": "Developed a responsive subscription website", "clarity": "Developed a responsive subscription website for individual real estate investment plans"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["State what the website enabled for subscribers or the business, only if verified.", "Add a verified scope or launch detail, such as subscriber counts or live status.", "Add evidence of the website''s use or launch, or keep the line to what was built."], "total": 5, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "d809791a6b4cd340", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(22,22,'bullet','{"en": "Automated the delivery process for new websites by reusing proven experience patterns, helping shorten release cycles.", "fr": "Automatisation de la livraison de nouveaux sites par la réutilisation de modèles éprouvés, réduisant les cycles de mise en production."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "helping shorten release cycles", "evidence": null, "contribution": "Automated the delivery process for new websites", "clarity": "Automated the delivery process for new websites by reusing proven experience patterns, helping shorten release cycles"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["Add a verified measure of the release-cycle change, only if one exists.", "Add evidence of the release-cycle change, or remove the shortening claim."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "c9baf5d1095b97a5", "scored_at": "2026-11-13"}');
INSERT INTO "bloc_descriptions" VALUES(23,23,'bullet','{"en": "Produced lead-capture websites that delivered strong conversion performance for client campaigns.", "fr": "Sites de génération de leads à forte conversion pour les campagnes clients."}','approved','2026-11-12 18:16:45','{"scores": {"result": 2, "evidence": 0, "contribution": 2, "clarity": 2}, "supporting_phrases": {"result": "delivered strong conversion performance for client campaigns", "evidence": null, "contribution": "Produced lead-capture websites", "clarity": "Produced lead-capture websites that delivered strong conversion performance"}, "evidence_type": "none", "claim_evidence_match": "missing", "attribution": "individual", "revision_requests": ["Add a verified conversion metric or client scope for the websites, only if one exists.", "Add evidence for the conversion performance claim, or replace ''strong'' with a verified figure."], "total": 6, "verdict": "Revise", "unquoted_phrases": [], "model": "claude-haiku-5-5", "via": "subagent", "version": 1, "text_hash": "bea033b234e783f8", "scored_at": "2026-11-13"}');
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
INSERT INTO "companies" VALUES(12,'{"en": "Theodo"}');
INSERT INTO "companies" VALUES(13,'{"en": "Oracle"}');
INSERT INTO "companies" VALUES(14,'{"en": "Y Strategie"}');
INSERT INTO "companies" VALUES(15,'{"en": "CGI"}');
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
INSERT INTO "compositions" VALUES(1,1,'jobs/theodo-software-engineer-fullstack-v1','Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','2026-11-06','2026-11-06','2026-11-11',NULL);
INSERT INTO "compositions" VALUES(2,2,'jobs/theodo-software-engineer-v1','Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','2026-11-08','2026-11-08','2026-11-11',NULL);
INSERT INTO "compositions" VALUES(3,3,'jobs/theodo-software-engineer-v2','Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','2026-11-08','2026-11-08','2026-11-11','dfcf8ca573bf37c22de25c4f50f025b39c716ee3dc3b1083f35b37f4fea076c5');
INSERT INTO "compositions" VALUES(4,4,'jobs/oracle-senior-manager-platform-software-engineering-v1','Mohamed-Amine-Sayagh-Senior-Manager-Platform-Software-Engineering-Oracle.pdf','2026-11-09','2026-11-09','2026-11-11',NULL);
INSERT INTO "compositions" VALUES(5,5,'jobs/y-strategie-senior-front-end-developer-v1','Mohamed-Amine-Sayagh-Senior-Front-End-Developer-Y-Strategie.pdf','2026-11-09','2026-11-09','2026-11-11','31dbade20293397aa6b1c43e776afedcfd5edd33e96411cc264be9e678293ba7');
INSERT INTO "compositions" VALUES(6,6,'jobs/oracle-software-development-manager-v1','Mohamed-Amine-Sayagh-Software-Development-Manager-Oracle.pdf','2026-11-10','2026-11-10','2026-11-11','9e065ff4ad4853ace22f595e3515612ee8f1256cc25b91f0eb12336f15971d6f');
INSERT INTO "compositions" VALUES(7,7,'jobs/oracle-senior-ai-software-engineer-v1','Mohamed-Amine-Sayagh-Senior-AI-Software-Engineer-Oracle.pdf','2026-11-10','2026-11-10','2026-11-11','9e065ff4ad4853ace22f595e3515612ee8f1256cc25b91f0eb12336f15971d6f');
INSERT INTO "compositions" VALUES(8,8,'jobs/cgi-senior-ai-engineer-java-spring-boot-h-f-v1','Mohamed-Amine-Sayagh-Senior-AI-Engineer-Java-Spring-Boot-H-F-CGI.pdf','2026-11-11','2026-11-11','2026-11-11','f3335ecb511d9b8dde24a9b92287bb5825b7ebf9084420c6201fceca3ab4a401');
INSERT INTO "compositions" VALUES(9,8,'jobs/cgi-senior-ai-engineer-java-spring-boot-h-f-v2','Mohamed-Amine-Sayagh-Senior-AI-Engineer-Java-Spring-Boot-H-F-CGI.pdf','2026-11-12 21:59:46','2026-11-12 21:59:46',NULL,NULL);
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
INSERT INTO "cover_paragraph_experiences" VALUES(3,5);
CREATE TABLE cover_paragraph_skills (
  paragraph_id INTEGER NOT NULL REFERENCES cover_paragraphs(id) ON DELETE CASCADE,
  skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (paragraph_id, skill_id)
);
INSERT INTO "cover_paragraph_skills" VALUES(1,2);
INSERT INTO "cover_paragraph_skills" VALUES(1,10);
INSERT INTO "cover_paragraph_skills" VALUES(1,82);
INSERT INTO "cover_paragraph_skills" VALUES(1,256);
INSERT INTO "cover_paragraph_skills" VALUES(2,82);
INSERT INTO "cover_paragraph_skills" VALUES(2,311);
INSERT INTO "cover_paragraph_skills" VALUES(2,340);
INSERT INTO "cover_paragraph_skills" VALUES(3,252);
INSERT INTO "cover_paragraph_skills" VALUES(3,256);
CREATE TABLE cover_paragraphs (
  id INTEGER PRIMARY KEY,
  part TEXT NOT NULL CHECK (part IN ('opening', 'example', 'support', 'close')),
  text TEXT NOT NULL,      -- json
  status TEXT NOT NULL DEFAULT 'approved' CHECK (status IN ('approved', 'rejected')),
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
INSERT INTO "cover_paragraphs" VALUES(1,'opening','{"en": "I am applying for the Senior AI Engineer / Java Spring Boot (H/F) role at CGI. My work has focused on building software that helps people carry out complex tasks, from campaign setup to security competitions.", "fr": "Je vous adresse ma candidature au poste de Senior AI Engineer / Java Spring Boot (H/F) chez CGI. Mon travail porte sur la conception de logiciels qui aident les utilisateurs à mener des tâches complexes, de la configuration de campagnes aux compétitions de sécurité."}','approved','2026-11-12 21:59:47');
INSERT INTO "cover_paragraphs" VALUES(2,'example','{"en": "At Hypeo, I integrated an AI agent experience that turns client conversations into configured marketing campaigns using an internal influencer database. Working closely with a senior technical lead, I refined the front-end experience as the backend integration and business requirements evolved.", "fr": "Chez Hypeo, j''ai intégré une expérience d''agent IA qui transforme les conversations clients en campagnes marketing configurées, à partir d''une base interne d''influenceurs. En étroite collaboration avec un lead technique senior, j''ai fait évoluer l''expérience front-end au rythme de l''intégration back-end et des besoins métier."}','approved','2026-11-12 21:59:47');
INSERT INTO "cover_paragraphs" VALUES(3,'support','{"en": "At Cyber Cohesion, I led web development for a security competition platform used at events including OWASP AppSec Days and BSides Singapore. I also developed its Warzone dashboard, which tracks team progress and scores.", "fr": "Chez Cyber Cohesion, j''ai dirigé le développement web d''une plateforme de compétitions de sécurité utilisée lors d''événements comme OWASP AppSec Days et BSides Singapore. J''ai également développé son tableau de bord Warzone, qui suit la progression et les scores des équipes."}','approved','2026-11-12 21:59:47');
INSERT INTO "cover_paragraphs" VALUES(4,'close','{"en": "I would welcome the opportunity to discuss how my experience could support the work at CGI. Thank you for your consideration.", "fr": "Je serais heureux d''échanger avec vous sur la manière dont mon expérience pourrait contribuer aux projets de CGI. Je vous prie d''agréer, Madame, Monsieur, l''expression de mes salutations distinguées."}','approved','2026-11-12 21:59:47');
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
INSERT INTO "interview_notes" VALUES(678,'draft text 2','2026-11-12 20:37:00');
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
INSERT INTO "offer_lines" VALUES(9,0,1);
INSERT INTO "offer_lines" VALUES(9,1,2);
INSERT INTO "offer_lines" VALUES(9,2,3);
INSERT INTO "offer_lines" VALUES(9,3,4);
INSERT INTO "offer_lines" VALUES(9,4,5);
INSERT INTO "offer_lines" VALUES(9,5,6);
INSERT INTO "offer_lines" VALUES(9,6,7);
INSERT INTO "offer_lines" VALUES(9,7,8);
INSERT INTO "offer_lines" VALUES(9,8,9);
INSERT INTO "offer_lines" VALUES(9,9,10);
INSERT INTO "offer_lines" VALUES(9,10,11);
INSERT INTO "offer_lines" VALUES(9,11,12);
INSERT INTO "offer_lines" VALUES(9,12,13);
INSERT INTO "offer_lines" VALUES(9,13,14);
INSERT INTO "offer_lines" VALUES(9,14,15);
INSERT INTO "offer_lines" VALUES(9,15,16);
INSERT INTO "offer_lines" VALUES(9,16,17);
INSERT INTO "offer_lines" VALUES(9,17,18);
INSERT INTO "offer_lines" VALUES(9,18,19);
INSERT INTO "offer_lines" VALUES(9,19,20);
INSERT INTO "offer_lines" VALUES(9,20,21);
INSERT INTO "offer_lines" VALUES(9,21,22);
INSERT INTO "offer_lines" VALUES(9,22,23);
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
INSERT INTO "offers" VALUES(1,12,'Software Engineer',NULL,'L’histoire du groupe Theodo et son succès
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
','fr',0,NULL,'2026-11-06','https://www.masayagh.com/resume/theodo/Mohamed-Amine-Sayagh-Software-Engineer-Fullstack-Theodo.pdf','{}');
INSERT INTO "offers" VALUES(2,12,'Software Engineer','https://jobs.lever.co/theodo/8f75eabb-5b64-4920-9630-1007429d1c9e','L’histoire du groupe Theodo et son succès
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
','fr',0,1,'2026-11-08','https://www.masayagh.com/resume/theodo/Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','{}');
INSERT INTO "offers" VALUES(3,12,'Software Engineer',NULL,'L’histoire du groupe Theodo et son succès
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
','fr',0,1,'2026-11-08','https://www.masayagh.com/resume/theodo/Mohamed-Amine-Sayagh-Software-Engineer-Theodo.pdf','{}');
INSERT INTO "offers" VALUES(4,13,'Senior Manager, Platform Software Engineering',NULL,'Job Description
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
','en',0,NULL,'2026-11-09','https://www.masayagh.com/resume/oracle/Mohamed-Amine-Sayagh-Senior-Manager-Platform-Software-Engineering-Oracle.pdf','{}');
INSERT INTO "offers" VALUES(5,14,'Senior Front-End Developer','https://ystrategie.teamtailor.com/jobs/8670374-senior-front-end-developer','Source: https://ystrategie.teamtailor.com/jobs/8670374-senior-front-end-developer
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
','en',0,1,'2026-11-09','https://www.masayagh.com/resume/y-strategie/Mohamed-Amine-Sayagh-Senior-Front-End-Developer-Y-Strategie.pdf','{}');
INSERT INTO "offers" VALUES(6,13,'Software Development Manager','https://careers.oracle.com/en/sites/jobsearch/job/344557/?utm_source=external%20referral&utm_medium=referral','Source: https://careers.oracle.com/en/sites/jobsearch/job/344557/?utm_source=external%20referral&utm_medium=referral
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
','en',1,1,'2026-11-10','https://www.masayagh.com/resume/oracle/Mohamed-Amine-Sayagh-Software-Development-Manager-Oracle.pdf','{}');
INSERT INTO "offers" VALUES(7,13,'Senior AI Software Engineer','https://careers.oracle.com/en/sites/jobsearch/job/338502/?utm_source=external%20referral&utm_medium=referral','Source: https://careers.oracle.com/en/sites/jobsearch/job/338502/?utm_source=external%20referral&utm_medium=referral
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
','en',0,1,'2026-11-10','https://www.masayagh.com/resume/oracle/Mohamed-Amine-Sayagh-Senior-AI-Software-Engineer-Oracle.pdf','{}');
INSERT INTO "offers" VALUES(8,15,'Senior AI Engineer / Java Spring Boot (H/F)','https://www.linkedin.com/jobs/view/4489607316?_l=en_US','Source: https://www.linkedin.com/jobs/view/4489607316?_l=en_US
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
','fr',0,1,'2026-11-11','https://www.masayagh.com/resume/cgi/Mohamed-Amine-Sayagh-Senior-AI-Engineer-Java-Spring-Boot-H-F-CGI.pdf','{}');
CREATE TABLE requirements (
  id INTEGER PRIMARY KEY,
  offer_id INTEGER NOT NULL REFERENCES offers(id) ON DELETE CASCADE,
  keyword_id INTEGER NOT NULL REFERENCES skill_keywords(id),
  priority INTEGER NOT NULL CHECK (priority BETWEEN 0 AND 100),
  min_years REAL CHECK (min_years IS NULL OR min_years > 0),
  UNIQUE (offer_id, keyword_id)
);
INSERT INTO "requirements" VALUES(398,1,28,0,NULL);
INSERT INTO "requirements" VALUES(399,1,29,0,NULL);
INSERT INTO "requirements" VALUES(400,1,32,0,NULL);
INSERT INTO "requirements" VALUES(401,1,33,0,NULL);
INSERT INTO "requirements" VALUES(402,1,34,0,NULL);
INSERT INTO "requirements" VALUES(403,1,2,0,NULL);
INSERT INTO "requirements" VALUES(404,1,10,0,NULL);
INSERT INTO "requirements" VALUES(405,1,7,0,NULL);
INSERT INTO "requirements" VALUES(406,1,35,0,NULL);
INSERT INTO "requirements" VALUES(407,1,5,0,NULL);
INSERT INTO "requirements" VALUES(408,1,3,0,NULL);
INSERT INTO "requirements" VALUES(409,1,38,100,NULL);
INSERT INTO "requirements" VALUES(410,1,39,100,NULL);
INSERT INTO "requirements" VALUES(411,1,40,100,NULL);
INSERT INTO "requirements" VALUES(412,1,41,100,NULL);
INSERT INTO "requirements" VALUES(413,1,42,100,NULL);
INSERT INTO "requirements" VALUES(414,1,43,100,NULL);
INSERT INTO "requirements" VALUES(415,1,44,100,NULL);
INSERT INTO "requirements" VALUES(416,1,45,100,NULL);
INSERT INTO "requirements" VALUES(417,1,46,100,NULL);
INSERT INTO "requirements" VALUES(418,1,47,100,NULL);
INSERT INTO "requirements" VALUES(419,1,48,100,NULL);
INSERT INTO "requirements" VALUES(420,1,49,100,NULL);
INSERT INTO "requirements" VALUES(421,1,50,100,NULL);
INSERT INTO "requirements" VALUES(422,1,51,100,NULL);
INSERT INTO "requirements" VALUES(423,1,52,100,NULL);
INSERT INTO "requirements" VALUES(424,1,53,100,NULL);
INSERT INTO "requirements" VALUES(425,3,55,0,NULL);
INSERT INTO "requirements" VALUES(426,3,375,0,NULL);
INSERT INTO "requirements" VALUES(427,3,57,0,NULL);
INSERT INTO "requirements" VALUES(428,3,376,0,NULL);
INSERT INTO "requirements" VALUES(429,3,377,0,NULL);
INSERT INTO "requirements" VALUES(430,3,46,0,NULL);
INSERT INTO "requirements" VALUES(431,3,60,0,NULL);
INSERT INTO "requirements" VALUES(432,3,61,100,NULL);
INSERT INTO "requirements" VALUES(433,3,62,100,5.0);
INSERT INTO "requirements" VALUES(434,3,63,0,NULL);
INSERT INTO "requirements" VALUES(435,3,64,100,1.0);
INSERT INTO "requirements" VALUES(436,4,66,0,NULL);
INSERT INTO "requirements" VALUES(437,4,65,0,NULL);
INSERT INTO "requirements" VALUES(438,4,67,0,NULL);
INSERT INTO "requirements" VALUES(439,4,69,0,NULL);
INSERT INTO "requirements" VALUES(440,4,70,0,NULL);
INSERT INTO "requirements" VALUES(441,4,71,0,NULL);
INSERT INTO "requirements" VALUES(442,4,378,0,NULL);
INSERT INTO "requirements" VALUES(443,4,379,100,NULL);
INSERT INTO "requirements" VALUES(444,4,380,100,NULL);
INSERT INTO "requirements" VALUES(445,4,76,0,NULL);
INSERT INTO "requirements" VALUES(446,4,381,0,NULL);
INSERT INTO "requirements" VALUES(447,4,84,0,NULL);
INSERT INTO "requirements" VALUES(448,4,86,0,NULL);
INSERT INTO "requirements" VALUES(449,4,382,0,NULL);
INSERT INTO "requirements" VALUES(450,4,105,0,NULL);
INSERT INTO "requirements" VALUES(451,4,77,100,NULL);
INSERT INTO "requirements" VALUES(452,4,78,100,NULL);
INSERT INTO "requirements" VALUES(453,4,79,100,NULL);
INSERT INTO "requirements" VALUES(454,4,80,0,NULL);
INSERT INTO "requirements" VALUES(455,4,383,0,NULL);
INSERT INTO "requirements" VALUES(456,4,384,0,NULL);
INSERT INTO "requirements" VALUES(457,4,82,0,NULL);
INSERT INTO "requirements" VALUES(458,4,83,0,NULL);
INSERT INTO "requirements" VALUES(459,4,85,0,NULL);
INSERT INTO "requirements" VALUES(460,4,87,100,NULL);
INSERT INTO "requirements" VALUES(461,4,88,0,NULL);
INSERT INTO "requirements" VALUES(462,4,89,0,NULL);
INSERT INTO "requirements" VALUES(463,4,90,0,NULL);
INSERT INTO "requirements" VALUES(464,4,385,0,NULL);
INSERT INTO "requirements" VALUES(465,4,91,0,NULL);
INSERT INTO "requirements" VALUES(466,4,92,0,NULL);
INSERT INTO "requirements" VALUES(467,4,93,0,NULL);
INSERT INTO "requirements" VALUES(468,4,94,0,NULL);
INSERT INTO "requirements" VALUES(469,4,95,100,NULL);
INSERT INTO "requirements" VALUES(470,4,96,0,NULL);
INSERT INTO "requirements" VALUES(471,4,98,0,NULL);
INSERT INTO "requirements" VALUES(472,4,99,100,NULL);
INSERT INTO "requirements" VALUES(473,4,100,0,NULL);
INSERT INTO "requirements" VALUES(474,4,68,0,NULL);
INSERT INTO "requirements" VALUES(475,4,101,0,NULL);
INSERT INTO "requirements" VALUES(476,4,386,0,NULL);
INSERT INTO "requirements" VALUES(477,4,103,0,NULL);
INSERT INTO "requirements" VALUES(478,4,104,0,NULL);
INSERT INTO "requirements" VALUES(479,4,140,0,NULL);
INSERT INTO "requirements" VALUES(480,4,387,0,NULL);
INSERT INTO "requirements" VALUES(481,4,107,0,NULL);
INSERT INTO "requirements" VALUES(482,4,108,0,NULL);
INSERT INTO "requirements" VALUES(483,4,109,0,NULL);
INSERT INTO "requirements" VALUES(484,4,110,100,NULL);
INSERT INTO "requirements" VALUES(485,4,111,100,NULL);
INSERT INTO "requirements" VALUES(486,4,112,100,NULL);
INSERT INTO "requirements" VALUES(487,4,113,100,NULL);
INSERT INTO "requirements" VALUES(488,4,114,100,NULL);
INSERT INTO "requirements" VALUES(489,4,388,100,NULL);
INSERT INTO "requirements" VALUES(490,4,389,100,NULL);
INSERT INTO "requirements" VALUES(491,4,117,100,NULL);
INSERT INTO "requirements" VALUES(492,4,118,100,NULL);
INSERT INTO "requirements" VALUES(493,4,119,100,NULL);
INSERT INTO "requirements" VALUES(494,4,120,100,NULL);
INSERT INTO "requirements" VALUES(495,4,121,100,NULL);
INSERT INTO "requirements" VALUES(496,4,390,100,NULL);
INSERT INTO "requirements" VALUES(497,4,391,100,NULL);
INSERT INTO "requirements" VALUES(498,4,308,100,NULL);
INSERT INTO "requirements" VALUES(499,4,392,0,NULL);
INSERT INTO "requirements" VALUES(500,4,125,0,NULL);
INSERT INTO "requirements" VALUES(501,4,126,0,NULL);
INSERT INTO "requirements" VALUES(502,4,127,0,NULL);
INSERT INTO "requirements" VALUES(503,4,128,0,NULL);
INSERT INTO "requirements" VALUES(504,4,129,0,NULL);
INSERT INTO "requirements" VALUES(505,4,393,0,NULL);
INSERT INTO "requirements" VALUES(506,4,130,0,NULL);
INSERT INTO "requirements" VALUES(507,4,131,0,NULL);
INSERT INTO "requirements" VALUES(508,4,132,0,NULL);
INSERT INTO "requirements" VALUES(509,4,296,0,NULL);
INSERT INTO "requirements" VALUES(510,4,134,0,NULL);
INSERT INTO "requirements" VALUES(511,4,135,0,NULL);
INSERT INTO "requirements" VALUES(512,4,394,0,NULL);
INSERT INTO "requirements" VALUES(513,4,137,0,NULL);
INSERT INTO "requirements" VALUES(514,4,395,0,NULL);
INSERT INTO "requirements" VALUES(515,4,138,0,NULL);
INSERT INTO "requirements" VALUES(516,4,139,0,NULL);
INSERT INTO "requirements" VALUES(517,4,309,0,NULL);
INSERT INTO "requirements" VALUES(518,4,142,100,NULL);
INSERT INTO "requirements" VALUES(519,4,143,100,NULL);
INSERT INTO "requirements" VALUES(520,4,144,100,NULL);
INSERT INTO "requirements" VALUES(521,4,145,100,NULL);
INSERT INTO "requirements" VALUES(522,5,148,0,NULL);
INSERT INTO "requirements" VALUES(523,5,396,0,NULL);
INSERT INTO "requirements" VALUES(524,5,149,100,NULL);
INSERT INTO "requirements" VALUES(525,5,150,0,NULL);
INSERT INTO "requirements" VALUES(526,5,397,100,NULL);
INSERT INTO "requirements" VALUES(527,5,152,0,NULL);
INSERT INTO "requirements" VALUES(528,5,153,0,NULL);
INSERT INTO "requirements" VALUES(529,5,154,0,NULL);
INSERT INTO "requirements" VALUES(530,5,155,0,NULL);
INSERT INTO "requirements" VALUES(531,5,151,0,NULL);
INSERT INTO "requirements" VALUES(532,5,156,0,NULL);
INSERT INTO "requirements" VALUES(533,5,398,0,NULL);
INSERT INTO "requirements" VALUES(534,5,399,0,NULL);
INSERT INTO "requirements" VALUES(535,5,157,100,NULL);
INSERT INTO "requirements" VALUES(536,5,400,0,NULL);
INSERT INTO "requirements" VALUES(537,5,159,0,NULL);
INSERT INTO "requirements" VALUES(538,5,160,0,NULL);
INSERT INTO "requirements" VALUES(539,5,43,0,NULL);
INSERT INTO "requirements" VALUES(540,5,401,0,NULL);
INSERT INTO "requirements" VALUES(541,5,161,0,NULL);
INSERT INTO "requirements" VALUES(542,5,402,0,NULL);
INSERT INTO "requirements" VALUES(543,5,403,0,NULL);
INSERT INTO "requirements" VALUES(544,5,404,100,5.0);
INSERT INTO "requirements" VALUES(545,5,164,100,2.0);
INSERT INTO "requirements" VALUES(546,5,165,100,NULL);
INSERT INTO "requirements" VALUES(547,5,166,100,NULL);
INSERT INTO "requirements" VALUES(548,5,167,100,NULL);
INSERT INTO "requirements" VALUES(549,5,405,100,NULL);
INSERT INTO "requirements" VALUES(550,5,168,100,NULL);
INSERT INTO "requirements" VALUES(551,5,406,100,NULL);
INSERT INTO "requirements" VALUES(552,5,170,100,NULL);
INSERT INTO "requirements" VALUES(553,5,171,100,NULL);
INSERT INTO "requirements" VALUES(554,5,407,100,NULL);
INSERT INTO "requirements" VALUES(555,5,87,100,NULL);
INSERT INTO "requirements" VALUES(556,5,172,100,NULL);
INSERT INTO "requirements" VALUES(557,5,1,100,NULL);
INSERT INTO "requirements" VALUES(558,5,173,100,NULL);
INSERT INTO "requirements" VALUES(559,5,408,100,NULL);
INSERT INTO "requirements" VALUES(560,5,174,100,NULL);
INSERT INTO "requirements" VALUES(561,5,409,100,NULL);
INSERT INTO "requirements" VALUES(562,5,176,100,NULL);
INSERT INTO "requirements" VALUES(563,5,177,100,NULL);
INSERT INTO "requirements" VALUES(564,5,410,100,NULL);
INSERT INTO "requirements" VALUES(565,5,178,100,NULL);
INSERT INTO "requirements" VALUES(566,5,411,100,NULL);
INSERT INTO "requirements" VALUES(567,5,179,100,NULL);
INSERT INTO "requirements" VALUES(568,5,16,100,NULL);
INSERT INTO "requirements" VALUES(569,5,412,100,NULL);
INSERT INTO "requirements" VALUES(570,5,181,100,NULL);
INSERT INTO "requirements" VALUES(571,5,182,100,NULL);
INSERT INTO "requirements" VALUES(572,5,183,100,NULL);
INSERT INTO "requirements" VALUES(573,5,184,100,NULL);
INSERT INTO "requirements" VALUES(574,5,413,100,NULL);
INSERT INTO "requirements" VALUES(575,5,185,100,NULL);
INSERT INTO "requirements" VALUES(576,5,186,100,NULL);
INSERT INTO "requirements" VALUES(577,5,187,100,NULL);
INSERT INTO "requirements" VALUES(578,5,188,100,NULL);
INSERT INTO "requirements" VALUES(579,5,189,0,NULL);
INSERT INTO "requirements" VALUES(580,5,414,0,NULL);
INSERT INTO "requirements" VALUES(581,5,415,0,NULL);
INSERT INTO "requirements" VALUES(582,5,416,0,NULL);
INSERT INTO "requirements" VALUES(583,5,17,0,NULL);
INSERT INTO "requirements" VALUES(584,5,190,0,NULL);
INSERT INTO "requirements" VALUES(585,5,191,0,NULL);
INSERT INTO "requirements" VALUES(586,5,192,0,NULL);
INSERT INTO "requirements" VALUES(587,5,193,0,NULL);
INSERT INTO "requirements" VALUES(588,5,194,0,NULL);
INSERT INTO "requirements" VALUES(589,5,417,0,NULL);
INSERT INTO "requirements" VALUES(590,5,196,0,NULL);
INSERT INTO "requirements" VALUES(591,5,197,0,NULL);
INSERT INTO "requirements" VALUES(592,5,418,0,NULL);
INSERT INTO "requirements" VALUES(593,5,198,0,NULL);
INSERT INTO "requirements" VALUES(594,5,199,0,NULL);
INSERT INTO "requirements" VALUES(595,5,200,0,NULL);
INSERT INTO "requirements" VALUES(596,5,201,0,NULL);
INSERT INTO "requirements" VALUES(597,5,202,0,NULL);
INSERT INTO "requirements" VALUES(598,5,203,0,NULL);
INSERT INTO "requirements" VALUES(599,5,204,0,NULL);
INSERT INTO "requirements" VALUES(600,6,205,100,NULL);
INSERT INTO "requirements" VALUES(601,6,206,100,NULL);
INSERT INTO "requirements" VALUES(602,6,78,0,NULL);
INSERT INTO "requirements" VALUES(603,6,207,0,NULL);
INSERT INTO "requirements" VALUES(604,6,208,0,NULL);
INSERT INTO "requirements" VALUES(605,6,209,0,NULL);
INSERT INTO "requirements" VALUES(606,6,210,100,NULL);
INSERT INTO "requirements" VALUES(607,6,419,100,NULL);
INSERT INTO "requirements" VALUES(608,6,385,100,NULL);
INSERT INTO "requirements" VALUES(609,6,420,100,NULL);
INSERT INTO "requirements" VALUES(610,6,213,0,NULL);
INSERT INTO "requirements" VALUES(611,6,325,0,NULL);
INSERT INTO "requirements" VALUES(612,6,421,0,NULL);
INSERT INTO "requirements" VALUES(613,6,216,0,NULL);
INSERT INTO "requirements" VALUES(614,6,422,0,NULL);
INSERT INTO "requirements" VALUES(615,6,218,0,NULL);
INSERT INTO "requirements" VALUES(616,6,423,0,NULL);
INSERT INTO "requirements" VALUES(617,6,225,0,NULL);
INSERT INTO "requirements" VALUES(618,6,226,0,NULL);
INSERT INTO "requirements" VALUES(619,6,227,0,NULL);
INSERT INTO "requirements" VALUES(620,6,100,0,NULL);
INSERT INTO "requirements" VALUES(621,6,139,0,NULL);
INSERT INTO "requirements" VALUES(622,6,424,0,NULL);
INSERT INTO "requirements" VALUES(623,6,115,0,NULL);
INSERT INTO "requirements" VALUES(624,6,89,0,NULL);
INSERT INTO "requirements" VALUES(625,6,232,0,NULL);
INSERT INTO "requirements" VALUES(626,6,425,0,NULL);
INSERT INTO "requirements" VALUES(627,6,426,0,NULL);
INSERT INTO "requirements" VALUES(628,6,427,0,NULL);
INSERT INTO "requirements" VALUES(629,6,80,0,NULL);
INSERT INTO "requirements" VALUES(630,6,91,0,NULL);
INSERT INTO "requirements" VALUES(631,6,236,0,NULL);
INSERT INTO "requirements" VALUES(632,6,237,0,NULL);
INSERT INTO "requirements" VALUES(633,6,238,0,NULL);
INSERT INTO "requirements" VALUES(634,6,239,0,NULL);
INSERT INTO "requirements" VALUES(635,6,241,0,NULL);
INSERT INTO "requirements" VALUES(636,6,242,0,NULL);
INSERT INTO "requirements" VALUES(637,6,308,100,NULL);
INSERT INTO "requirements" VALUES(638,6,310,100,NULL);
INSERT INTO "requirements" VALUES(639,6,428,100,NULL);
INSERT INTO "requirements" VALUES(640,6,245,100,10.0);
INSERT INTO "requirements" VALUES(641,6,429,100,5.0);
INSERT INTO "requirements" VALUES(642,6,249,100,5.0);
INSERT INTO "requirements" VALUES(643,6,430,100,NULL);
INSERT INTO "requirements" VALUES(644,6,72,100,NULL);
INSERT INTO "requirements" VALUES(645,6,254,100,NULL);
INSERT INTO "requirements" VALUES(646,6,120,100,NULL);
INSERT INTO "requirements" VALUES(647,6,255,100,NULL);
INSERT INTO "requirements" VALUES(648,6,256,100,NULL);
INSERT INTO "requirements" VALUES(649,6,257,100,NULL);
INSERT INTO "requirements" VALUES(650,6,260,100,NULL);
INSERT INTO "requirements" VALUES(651,6,262,100,NULL);
INSERT INTO "requirements" VALUES(652,6,264,100,NULL);
INSERT INTO "requirements" VALUES(653,6,265,100,NULL);
INSERT INTO "requirements" VALUES(654,6,266,100,NULL);
INSERT INTO "requirements" VALUES(655,6,431,100,NULL);
INSERT INTO "requirements" VALUES(656,6,268,0,NULL);
INSERT INTO "requirements" VALUES(657,6,269,0,NULL);
INSERT INTO "requirements" VALUES(658,6,119,0,NULL);
INSERT INTO "requirements" VALUES(659,6,273,0,NULL);
INSERT INTO "requirements" VALUES(660,6,274,0,NULL);
INSERT INTO "requirements" VALUES(661,6,275,0,NULL);
INSERT INTO "requirements" VALUES(662,6,276,0,NULL);
INSERT INTO "requirements" VALUES(663,6,277,0,NULL);
INSERT INTO "requirements" VALUES(664,6,432,0,NULL);
INSERT INTO "requirements" VALUES(665,6,433,0,NULL);
INSERT INTO "requirements" VALUES(666,6,278,0,NULL);
INSERT INTO "requirements" VALUES(667,6,279,0,NULL);
INSERT INTO "requirements" VALUES(668,6,280,0,NULL);
INSERT INTO "requirements" VALUES(669,7,341,100,NULL);
INSERT INTO "requirements" VALUES(670,7,281,100,NULL);
INSERT INTO "requirements" VALUES(671,7,282,100,NULL);
INSERT INTO "requirements" VALUES(672,7,283,100,NULL);
INSERT INTO "requirements" VALUES(673,7,434,0,NULL);
INSERT INTO "requirements" VALUES(674,7,284,0,NULL);
INSERT INTO "requirements" VALUES(675,7,435,0,NULL);
INSERT INTO "requirements" VALUES(676,7,285,0,NULL);
INSERT INTO "requirements" VALUES(677,7,286,0,NULL);
INSERT INTO "requirements" VALUES(678,7,245,100,NULL);
INSERT INTO "requirements" VALUES(679,7,287,0,NULL);
INSERT INTO "requirements" VALUES(680,7,288,100,NULL);
INSERT INTO "requirements" VALUES(681,7,289,100,NULL);
INSERT INTO "requirements" VALUES(682,7,290,100,NULL);
INSERT INTO "requirements" VALUES(683,7,291,0,NULL);
INSERT INTO "requirements" VALUES(684,7,98,0,NULL);
INSERT INTO "requirements" VALUES(685,7,293,0,NULL);
INSERT INTO "requirements" VALUES(686,7,295,0,NULL);
INSERT INTO "requirements" VALUES(687,7,99,100,NULL);
INSERT INTO "requirements" VALUES(688,7,296,100,NULL);
INSERT INTO "requirements" VALUES(689,7,298,0,NULL);
INSERT INTO "requirements" VALUES(690,7,128,100,NULL);
INSERT INTO "requirements" VALUES(691,7,100,100,NULL);
INSERT INTO "requirements" VALUES(692,7,303,0,NULL);
INSERT INTO "requirements" VALUES(693,7,302,100,NULL);
INSERT INTO "requirements" VALUES(694,7,304,0,NULL);
INSERT INTO "requirements" VALUES(695,7,307,0,NULL);
INSERT INTO "requirements" VALUES(696,7,436,100,NULL);
INSERT INTO "requirements" VALUES(697,7,437,100,NULL);
INSERT INTO "requirements" VALUES(698,7,311,0,NULL);
INSERT INTO "requirements" VALUES(699,7,252,0,NULL);
INSERT INTO "requirements" VALUES(700,7,312,0,NULL);
INSERT INTO "requirements" VALUES(701,7,313,0,NULL);
INSERT INTO "requirements" VALUES(702,7,2,100,NULL);
INSERT INTO "requirements" VALUES(703,7,3,100,NULL);
INSERT INTO "requirements" VALUES(704,7,314,100,NULL);
INSERT INTO "requirements" VALUES(705,7,315,100,NULL);
INSERT INTO "requirements" VALUES(706,7,316,100,NULL);
INSERT INTO "requirements" VALUES(707,7,317,100,NULL);
INSERT INTO "requirements" VALUES(708,7,213,100,NULL);
INSERT INTO "requirements" VALUES(709,7,318,100,NULL);
INSERT INTO "requirements" VALUES(710,7,319,100,NULL);
INSERT INTO "requirements" VALUES(711,7,320,100,NULL);
INSERT INTO "requirements" VALUES(712,7,321,100,NULL);
INSERT INTO "requirements" VALUES(713,7,322,100,NULL);
INSERT INTO "requirements" VALUES(714,7,323,100,NULL);
INSERT INTO "requirements" VALUES(715,7,324,100,NULL);
INSERT INTO "requirements" VALUES(716,7,325,100,NULL);
INSERT INTO "requirements" VALUES(717,7,326,100,NULL);
INSERT INTO "requirements" VALUES(718,7,16,100,NULL);
INSERT INTO "requirements" VALUES(719,7,327,100,NULL);
INSERT INTO "requirements" VALUES(720,7,438,100,NULL);
INSERT INTO "requirements" VALUES(721,7,160,100,NULL);
INSERT INTO "requirements" VALUES(722,7,172,100,NULL);
INSERT INTO "requirements" VALUES(723,7,306,100,NULL);
INSERT INTO "requirements" VALUES(724,7,328,100,NULL);
INSERT INTO "requirements" VALUES(725,7,236,100,NULL);
INSERT INTO "requirements" VALUES(726,7,264,100,NULL);
INSERT INTO "requirements" VALUES(727,7,329,100,NULL);
INSERT INTO "requirements" VALUES(728,7,330,0,NULL);
INSERT INTO "requirements" VALUES(729,7,331,0,NULL);
INSERT INTO "requirements" VALUES(730,7,101,0,NULL);
INSERT INTO "requirements" VALUES(731,7,120,0,NULL);
INSERT INTO "requirements" VALUES(732,7,332,0,NULL);
INSERT INTO "requirements" VALUES(733,7,333,0,NULL);
INSERT INTO "requirements" VALUES(734,7,334,0,NULL);
INSERT INTO "requirements" VALUES(735,7,335,0,NULL);
INSERT INTO "requirements" VALUES(736,7,336,0,NULL);
INSERT INTO "requirements" VALUES(737,7,337,0,NULL);
INSERT INTO "requirements" VALUES(738,7,338,0,NULL);
INSERT INTO "requirements" VALUES(739,7,69,0,NULL);
INSERT INTO "requirements" VALUES(740,7,339,0,NULL);
INSERT INTO "requirements" VALUES(741,7,340,0,NULL);
INSERT INTO "requirements" VALUES(742,7,439,0,NULL);
INSERT INTO "requirements" VALUES(743,7,440,0,NULL);
INSERT INTO "requirements" VALUES(744,7,441,100,NULL);
INSERT INTO "requirements" VALUES(745,8,345,100,2.0);
INSERT INTO "requirements" VALUES(746,8,347,0,NULL);
INSERT INTO "requirements" VALUES(747,8,348,0,NULL);
INSERT INTO "requirements" VALUES(748,8,442,0,NULL);
INSERT INTO "requirements" VALUES(749,8,349,100,NULL);
INSERT INTO "requirements" VALUES(750,8,2,100,10.0);
INSERT INTO "requirements" VALUES(751,8,10,100,10.0);
INSERT INTO "requirements" VALUES(752,8,351,100,NULL);
INSERT INTO "requirements" VALUES(753,8,352,100,NULL);
INSERT INTO "requirements" VALUES(754,8,353,0,NULL);
INSERT INTO "requirements" VALUES(755,8,355,100,NULL);
INSERT INTO "requirements" VALUES(756,8,356,100,NULL);
INSERT INTO "requirements" VALUES(757,8,357,0,NULL);
INSERT INTO "requirements" VALUES(758,8,358,0,NULL);
INSERT INTO "requirements" VALUES(759,8,359,0,NULL);
INSERT INTO "requirements" VALUES(760,8,42,0,NULL);
INSERT INTO "requirements" VALUES(761,8,360,0,NULL);
INSERT INTO "requirements" VALUES(762,8,50,0,NULL);
INSERT INTO "requirements" VALUES(763,8,16,100,NULL);
INSERT INTO "requirements" VALUES(764,8,361,0,NULL);
INSERT INTO "requirements" VALUES(765,8,362,100,NULL);
INSERT INTO "requirements" VALUES(766,8,363,100,NULL);
INSERT INTO "requirements" VALUES(767,8,364,100,2.0);
INSERT INTO "requirements" VALUES(768,8,350,100,NULL);
INSERT INTO "requirements" VALUES(769,8,178,100,NULL);
INSERT INTO "requirements" VALUES(770,8,28,100,NULL);
INSERT INTO "requirements" VALUES(771,8,365,100,NULL);
INSERT INTO "requirements" VALUES(772,8,366,100,NULL);
INSERT INTO "requirements" VALUES(773,8,367,100,NULL);
INSERT INTO "requirements" VALUES(774,8,368,100,NULL);
INSERT INTO "requirements" VALUES(775,8,369,100,NULL);
INSERT INTO "requirements" VALUES(776,8,370,100,NULL);
INSERT INTO "requirements" VALUES(777,8,52,100,NULL);
INSERT INTO "requirements" VALUES(778,8,371,100,NULL);
INSERT INTO "requirements" VALUES(779,8,372,100,NULL);
INSERT INTO "requirements" VALUES(780,8,373,100,NULL);
INSERT INTO "requirements" VALUES(781,8,374,100,NULL);
INSERT INTO "requirements" VALUES(782,8,441,100,NULL);
INSERT INTO "requirements" VALUES(783,2,441,100,NULL);
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
INSERT INTO "skill_keywords" VALUES(28,28,'tests','en');
INSERT INTO "skill_keywords" VALUES(29,29,'refactoring','en');
INSERT INTO "skill_keywords" VALUES(32,32,'débugger','en');
INSERT INTO "skill_keywords" VALUES(33,33,'résolution de problèmes','en');
INSERT INTO "skill_keywords" VALUES(34,34,'llm','en');
INSERT INTO "skill_keywords" VALUES(35,35,'node','en');
INSERT INTO "skill_keywords" VALUES(38,38,'top école d''ingénieur','en');
INSERT INTO "skill_keywords" VALUES(39,39,'travailler en équipe','en');
INSERT INTO "skill_keywords" VALUES(40,40,'pédagogie','en');
INSERT INTO "skill_keywords" VALUES(41,41,'esprit constructif','en');
INSERT INTO "skill_keywords" VALUES(42,42,'revues de code','en');
INSERT INTO "skill_keywords" VALUES(43,43,'pair programming','en');
INSERT INTO "skill_keywords" VALUES(44,44,'création de valeur','en');
INSERT INTO "skill_keywords" VALUES(45,45,'genai','en');
INSERT INTO "skill_keywords" VALUES(46,46,'veille technique','en');
INSERT INTO "skill_keywords" VALUES(47,47,'exigence sur la qualité','en');
INSERT INTO "skill_keywords" VALUES(48,48,'jidoka','en');
INSERT INTO "skill_keywords" VALUES(49,49,'travailler de manière structurée','en');
INSERT INTO "skill_keywords" VALUES(50,50,'amélioration continue','en');
INSERT INTO "skill_keywords" VALUES(51,51,'5s','en');
INSERT INTO "skill_keywords" VALUES(52,52,'esprit d''équipe','en');
INSERT INTO "skill_keywords" VALUES(53,53,'prise d''initiative','en');
INSERT INTO "skill_keywords" VALUES(55,55,'conception','en');
INSERT INTO "skill_keywords" VALUES(57,57,'qualité','en');
INSERT INTO "skill_keywords" VALUES(60,60,'craftsmanship','en');
INSERT INTO "skill_keywords" VALUES(61,61,'école d''ingénieur','en');
INSERT INTO "skill_keywords" VALUES(62,62,'développement de logiciels','en');
INSERT INTO "skill_keywords" VALUES(63,63,'fullstack','en');
INSERT INTO "skill_keywords" VALUES(64,64,'gestion d''une équipe','en');
INSERT INTO "skill_keywords" VALUES(65,65,'middleware','en');
INSERT INTO "skill_keywords" VALUES(66,66,'platform teams','en');
INSERT INTO "skill_keywords" VALUES(67,67,'distributed debugging','en');
INSERT INTO "skill_keywords" VALUES(68,68,'reliability','en');
INSERT INTO "skill_keywords" VALUES(69,69,'observability','en');
INSERT INTO "skill_keywords" VALUES(70,70,'slos','en');
INSERT INTO "skill_keywords" VALUES(71,71,'resilience patterns','en');
INSERT INTO "skill_keywords" VALUES(72,72,'stakeholders','en');
INSERT INTO "skill_keywords" VALUES(76,76,'morocco','en');
INSERT INTO "skill_keywords" VALUES(77,77,'engineering leader','en');
INSERT INTO "skill_keywords" VALUES(78,78,'people leadership','en');
INSERT INTO "skill_keywords" VALUES(79,79,'technical judgement','en');
INSERT INTO "skill_keywords" VALUES(80,80,'ai technologies','en');
INSERT INTO "skill_keywords" VALUES(82,82,'ai','en');
INSERT INTO "skill_keywords" VALUES(83,83,'full-stack development','en');
INSERT INTO "skill_keywords" VALUES(84,84,'application infrastructure','en');
INSERT INTO "skill_keywords" VALUES(85,85,'developer tooling','en');
INSERT INTO "skill_keywords" VALUES(86,86,'ui frameworks','en');
INSERT INTO "skill_keywords" VALUES(87,87,'coaching','en');
INSERT INTO "skill_keywords" VALUES(88,88,'feedback','en');
INSERT INTO "skill_keywords" VALUES(89,89,'performance management','en');
INSERT INTO "skill_keywords" VALUES(90,90,'technical leaders','en');
INSERT INTO "skill_keywords" VALUES(91,91,'collaborative','en');
INSERT INTO "skill_keywords" VALUES(92,92,'accountable','en');
INSERT INTO "skill_keywords" VALUES(93,93,'ai-enabled applications','en');
INSERT INTO "skill_keywords" VALUES(94,94,'full-stack services','en');
INSERT INTO "skill_keywords" VALUES(95,95,'developer platforms','en');
INSERT INTO "skill_keywords" VALUES(96,96,'scalable software','en');
INSERT INTO "skill_keywords" VALUES(98,98,'architecture','en');
INSERT INTO "skill_keywords" VALUES(99,99,'apis','en');
INSERT INTO "skill_keywords" VALUES(100,100,'testing','en');
INSERT INTO "skill_keywords" VALUES(101,101,'distributed systems','en');
INSERT INTO "skill_keywords" VALUES(103,103,'platform performance','en');
INSERT INTO "skill_keywords" VALUES(104,104,'resilience','en');
INSERT INTO "skill_keywords" VALUES(105,105,'matrixed model','en');
INSERT INTO "skill_keywords" VALUES(107,107,'trusted relationships','en');
INSERT INTO "skill_keywords" VALUES(108,108,'communicate','en');
INSERT INTO "skill_keywords" VALUES(109,109,'adapt','en');
INSERT INTO "skill_keywords" VALUES(110,110,'full-stack software development','en');
INSERT INTO "skill_keywords" VALUES(111,111,'front-end technologies','en');
INSERT INTO "skill_keywords" VALUES(112,112,'service development','en');
INSERT INTO "skill_keywords" VALUES(113,113,'data integration','en');
INSERT INTO "skill_keywords" VALUES(114,114,'cloud-based application architectures','en');
INSERT INTO "skill_keywords" VALUES(115,115,'hiring','en');
INSERT INTO "skill_keywords" VALUES(117,117,'matrixed organisation','en');
INSERT INTO "skill_keywords" VALUES(118,118,'shared accountability','en');
INSERT INTO "skill_keywords" VALUES(119,119,'enterprise software','en');
INSERT INTO "skill_keywords" VALUES(120,120,'cloud services','en');
INSERT INTO "skill_keywords" VALUES(121,121,'frameworks','en');
INSERT INTO "skill_keywords" VALUES(125,125,'agentic systems','en');
INSERT INTO "skill_keywords" VALUES(126,126,'generative ai platforms','en');
INSERT INTO "skill_keywords" VALUES(127,127,'ai-assisted developer tools','en');
INSERT INTO "skill_keywords" VALUES(128,128,'large language models','en');
INSERT INTO "skill_keywords" VALUES(129,129,'agent orchestration','en');
INSERT INTO "skill_keywords" VALUES(130,130,'model evaluation','en');
INSERT INTO "skill_keywords" VALUES(131,131,'ai guardrails','en');
INSERT INTO "skill_keywords" VALUES(132,132,'ai observability','en');
INSERT INTO "skill_keywords" VALUES(134,134,'developer tools','en');
INSERT INTO "skill_keywords" VALUES(135,135,'internal engineering platforms','en');
INSERT INTO "skill_keywords" VALUES(137,137,'multicultural engineering teams','en');
INSERT INTO "skill_keywords" VALUES(138,138,'site reliability engineering','en');
INSERT INTO "skill_keywords" VALUES(139,139,'incident management','en');
INSERT INTO "skill_keywords" VALUES(140,140,'operational readiness','en');
INSERT INTO "skill_keywords" VALUES(142,142,'application platforms','en');
INSERT INTO "skill_keywords" VALUES(143,143,'platform development','en');
INSERT INTO "skill_keywords" VALUES(144,144,'software management','en');
INSERT INTO "skill_keywords" VALUES(145,145,'software platform development','en');
INSERT INTO "skill_keywords" VALUES(148,148,'api endpoints','en');
INSERT INTO "skill_keywords" VALUES(149,149,'jquery','en');
INSERT INTO "skill_keywords" VALUES(150,150,'vue 3','en');
INSERT INTO "skill_keywords" VALUES(151,151,'component libraries','en');
INSERT INTO "skill_keywords" VALUES(152,152,'front-end ecosystem','en');
INSERT INTO "skill_keywords" VALUES(153,153,'component library','en');
INSERT INTO "skill_keywords" VALUES(154,154,'documenting components','en');
INSERT INTO "skill_keywords" VALUES(155,155,'modular components','en');
INSERT INTO "skill_keywords" VALUES(156,156,'component architecture','en');
INSERT INTO "skill_keywords" VALUES(157,157,'api design','en');
INSERT INTO "skill_keywords" VALUES(159,159,'mentor','en');
INSERT INTO "skill_keywords" VALUES(160,160,'code reviews','en');
INSERT INTO "skill_keywords" VALUES(161,161,'accessibility','en');
INSERT INTO "skill_keywords" VALUES(164,164,'vue 3 composition api','en');
INSERT INTO "skill_keywords" VALUES(165,165,'tailwind css','en');
INSERT INTO "skill_keywords" VALUES(166,166,'responsive uis','en');
INSERT INTO "skill_keywords" VALUES(167,167,'html markup','en');
INSERT INTO "skill_keywords" VALUES(168,168,'design systems','en');
INSERT INTO "skill_keywords" VALUES(170,170,'api development','en');
INSERT INTO "skill_keywords" VALUES(171,171,'laravel endpoints','en');
INSERT INTO "skill_keywords" VALUES(172,172,'mentoring','en');
INSERT INTO "skill_keywords" VALUES(173,173,'typescript','en');
INSERT INTO "skill_keywords" VALUES(174,174,'html5','en');
INSERT INTO "skill_keywords" VALUES(176,176,'scss','en');
INSERT INTO "skill_keywords" VALUES(177,177,'sass','en');
INSERT INTO "skill_keywords" VALUES(178,178,'git','en');
INSERT INTO "skill_keywords" VALUES(179,179,'git workflow','en');
INSERT INTO "skill_keywords" VALUES(181,181,'scalable, reusable solutions','en');
INSERT INTO "skill_keywords" VALUES(182,182,'collaborator','en');
INSERT INTO "skill_keywords" VALUES(183,183,'patient','en');
INSERT INTO "skill_keywords" VALUES(184,184,'supportive','en');
INSERT INTO "skill_keywords" VALUES(185,185,'remotely','en');
INSERT INTO "skill_keywords" VALUES(186,186,'self-motivated','en');
INSERT INTO "skill_keywords" VALUES(187,187,'communicative','en');
INSERT INTO "skill_keywords" VALUES(188,188,'pragmatism','en');
INSERT INTO "skill_keywords" VALUES(189,189,'laravel ecosystem','en');
INSERT INTO "skill_keywords" VALUES(190,190,'wamp','en');
INSERT INTO "skill_keywords" VALUES(191,191,'lamp','en');
INSERT INTO "skill_keywords" VALUES(192,192,'pinia','en');
INSERT INTO "skill_keywords" VALUES(193,193,'vue state management','en');
INSERT INTO "skill_keywords" VALUES(194,194,'veevalidate','en');
INSERT INTO "skill_keywords" VALUES(196,196,'maizzle','en');
INSERT INTO "skill_keywords" VALUES(197,197,'ai/ml','en');
INSERT INTO "skill_keywords" VALUES(198,198,'ui design','en');
INSERT INTO "skill_keywords" VALUES(199,199,'ux','en');
INSERT INTO "skill_keywords" VALUES(200,200,'rapidly prototype','en');
INSERT INTO "skill_keywords" VALUES(201,201,'testing frameworks','en');
INSERT INTO "skill_keywords" VALUES(202,202,'jest','en');
INSERT INTO "skill_keywords" VALUES(203,203,'vitest','en');
INSERT INTO "skill_keywords" VALUES(204,204,'cypress','en');
INSERT INTO "skill_keywords" VALUES(205,205,'software development manager','en');
INSERT INTO "skill_keywords" VALUES(206,206,'engineering organization','en');
INSERT INTO "skill_keywords" VALUES(207,207,'engineering execution','en');
INSERT INTO "skill_keywords" VALUES(208,208,'operational excellence','en');
INSERT INTO "skill_keywords" VALUES(209,209,'talent development','en');
INSERT INTO "skill_keywords" VALUES(210,210,'engineering judgment','en');
INSERT INTO "skill_keywords" VALUES(213,213,'software architecture','en');
INSERT INTO "skill_keywords" VALUES(216,216,'databases','en');
INSERT INTO "skill_keywords" VALUES(218,218,'operating model','en');
INSERT INTO "skill_keywords" VALUES(225,225,'customer focus','en');
INSERT INTO "skill_keywords" VALUES(226,226,'engineering best practices','en');
INSERT INTO "skill_keywords" VALUES(227,227,'architecture reviews','en');
INSERT INTO "skill_keywords" VALUES(232,232,'succession planning','en');
INSERT INTO "skill_keywords" VALUES(236,236,'ownership','en');
INSERT INTO "skill_keywords" VALUES(237,237,'innovation','en');
INSERT INTO "skill_keywords" VALUES(238,238,'transparent communication','en');
INSERT INTO "skill_keywords" VALUES(239,239,'cross-functional planning','en');
INSERT INTO "skill_keywords" VALUES(241,241,'budgets','en');
INSERT INTO "skill_keywords" VALUES(242,242,'vendor relationships','en');
INSERT INTO "skill_keywords" VALUES(245,245,'software engineering','en');
INSERT INTO "skill_keywords" VALUES(249,249,'managing managers','en');
INSERT INTO "skill_keywords" VALUES(252,252,'platform','en');
INSERT INTO "skill_keywords" VALUES(254,254,'modern software development practices','en');
INSERT INTO "skill_keywords" VALUES(255,255,'operational reliability','en');
INSERT INTO "skill_keywords" VALUES(256,256,'security','en');
INSERT INTO "skill_keywords" VALUES(257,257,'agile delivery','en');
INSERT INTO "skill_keywords" VALUES(260,260,'incident response','en');
INSERT INTO "skill_keywords" VALUES(262,262,'translate business and customer needs','en');
INSERT INTO "skill_keywords" VALUES(264,264,'communication','en');
INSERT INTO "skill_keywords" VALUES(265,265,'stakeholder-management','en');
INSERT INTO "skill_keywords" VALUES(266,266,'organizational leadership','en');
INSERT INTO "skill_keywords" VALUES(268,268,'french','en');
INSERT INTO "skill_keywords" VALUES(269,269,'arabic','en');
INSERT INTO "skill_keywords" VALUES(273,273,'machine learning','en');
INSERT INTO "skill_keywords" VALUES(274,274,'generative ai','en');
INSERT INTO "skill_keywords" VALUES(275,275,'global, distributed engineering organization','en');
INSERT INTO "skill_keywords" VALUES(276,276,'building or scaling engineering teams','en');
INSERT INTO "skill_keywords" VALUES(277,277,'emea','en');
INSERT INTO "skill_keywords" VALUES(278,278,'workforce planning','en');
INSERT INTO "skill_keywords" VALUES(279,279,'organizational design','en');
INSERT INTO "skill_keywords" VALUES(280,280,'budget management','en');
INSERT INTO "skill_keywords" VALUES(281,281,'coding ability','en');
INSERT INTO "skill_keywords" VALUES(282,282,'technical judgment','en');
INSERT INTO "skill_keywords" VALUES(283,283,'lead engineering work','en');
INSERT INTO "skill_keywords" VALUES(284,284,'reviewing code','en');
INSERT INTO "skill_keywords" VALUES(285,285,'driving execution','en');
INSERT INTO "skill_keywords" VALUES(286,286,'ai capabilities','en');
INSERT INTO "skill_keywords" VALUES(287,287,'technical leadership','en');
INSERT INTO "skill_keywords" VALUES(288,288,'large codebases','en');
INSERT INTO "skill_keywords" VALUES(289,289,'design reliable systems','en');
INSERT INTO "skill_keywords" VALUES(290,290,'production-ready features','en');
INSERT INTO "skill_keywords" VALUES(291,291,'ai-enabled product capabilities','en');
INSERT INTO "skill_keywords" VALUES(293,293,'production-grade software','en');
INSERT INTO "skill_keywords" VALUES(295,295,'scalable services','en');
INSERT INTO "skill_keywords" VALUES(296,296,'sdks','en');
INSERT INTO "skill_keywords" VALUES(298,298,'technical designs','en');
INSERT INTO "skill_keywords" VALUES(302,302,'design review','en');
INSERT INTO "skill_keywords" VALUES(303,303,'code changes','en');
INSERT INTO "skill_keywords" VALUES(304,304,'lead engineering execution','en');
INSERT INTO "skill_keywords" VALUES(306,306,'engineering planning','en');
INSERT INTO "skill_keywords" VALUES(307,307,'mentor engineers','en');
INSERT INTO "skill_keywords" VALUES(308,308,'bachelor''s degree','en');
INSERT INTO "skill_keywords" VALUES(309,309,'master''s degree','en');
INSERT INTO "skill_keywords" VALUES(310,310,'computer science','en');
INSERT INTO "skill_keywords" VALUES(311,311,'backend','en');
INSERT INTO "skill_keywords" VALUES(312,312,'infrastructure','en');
INSERT INTO "skill_keywords" VALUES(313,313,'enterprise product development','en');
INSERT INTO "skill_keywords" VALUES(314,314,'c++','en');
INSERT INTO "skill_keywords" VALUES(315,315,'data structures','en');
INSERT INTO "skill_keywords" VALUES(316,316,'algorithms','en');
INSERT INTO "skill_keywords" VALUES(317,317,'system design','en');
INSERT INTO "skill_keywords" VALUES(318,318,'production-grade services','en');
INSERT INTO "skill_keywords" VALUES(319,319,'libraries','en');
INSERT INTO "skill_keywords" VALUES(320,320,'platform components','en');
INSERT INTO "skill_keywords" VALUES(321,321,'large, complex codebases','en');
INSERT INTO "skill_keywords" VALUES(322,322,'ai systems','en');
INSERT INTO "skill_keywords" VALUES(323,323,'ai application development','en');
INSERT INTO "skill_keywords" VALUES(324,324,'ai platform integration','en');
INSERT INTO "skill_keywords" VALUES(325,325,'debugging','en');
INSERT INTO "skill_keywords" VALUES(326,326,'performance analysis','en');
INSERT INTO "skill_keywords" VALUES(327,327,'production support','en');
INSERT INTO "skill_keywords" VALUES(328,328,'problem-solving','en');
INSERT INTO "skill_keywords" VALUES(329,329,'collaboration','en');
INSERT INTO "skill_keywords" VALUES(330,330,'ai-enabled enterprise applications','en');
INSERT INTO "skill_keywords" VALUES(331,331,'ai platform capabilities','en');
INSERT INTO "skill_keywords" VALUES(332,332,'large-scale backend platforms','en');
INSERT INTO "skill_keywords" VALUES(333,333,'developer-facing tools','en');
INSERT INTO "skill_keywords" VALUES(334,334,'internal engineering frameworks','en');
INSERT INTO "skill_keywords" VALUES(335,335,'llm orchestration','en');
INSERT INTO "skill_keywords" VALUES(336,336,'evaluation','en');
INSERT INTO "skill_keywords" VALUES(337,337,'rag','en');
INSERT INTO "skill_keywords" VALUES(338,338,'agentic workflows','en');
INSERT INTO "skill_keywords" VALUES(339,339,'ai governance','en');
INSERT INTO "skill_keywords" VALUES(340,340,'technical lead','en');
INSERT INTO "skill_keywords" VALUES(341,341,'senior engineer','en');
INSERT INTO "skill_keywords" VALUES(345,345,'intelligence artificielle','en');
INSERT INTO "skill_keywords" VALUES(347,347,'architecture back-end','en');
INSERT INTO "skill_keywords" VALUES(348,348,'architectures distribuées','en');
INSERT INTO "skill_keywords" VALUES(349,349,'ia agentique','en');
INSERT INTO "skill_keywords" VALUES(350,350,'architectures back-end','en');
INSERT INTO "skill_keywords" VALUES(351,351,'microservices','en');
INSERT INTO "skill_keywords" VALUES(352,352,'event-driven','en');
INSERT INTO "skill_keywords" VALUES(353,353,'composants ia','en');
INSERT INTO "skill_keywords" VALUES(355,355,'bases de données relationnelles','en');
INSERT INTO "skill_keywords" VALUES(356,356,'bases de données documentaires','en');
INSERT INTO "skill_keywords" VALUES(357,357,'choix d''architecture','en');
INSERT INTO "skill_keywords" VALUES(358,358,'sécurité','en');
INSERT INTO "skill_keywords" VALUES(359,359,'maintenabilité','en');
INSERT INTO "skill_keywords" VALUES(360,360,'tests techniques','en');
INSERT INTO "skill_keywords" VALUES(361,361,'accompagner les équipes techniques','en');
INSERT INTO "skill_keywords" VALUES(362,362,'formation supérieure en informatique','en');
INSERT INTO "skill_keywords" VALUES(363,363,'bac+5','en');
INSERT INTO "skill_keywords" VALUES(364,364,'ai building','en');
INSERT INTO "skill_keywords" VALUES(365,365,'sonar','en');
INSERT INTO "skill_keywords" VALUES(366,366,'capacité d''analyse','en');
INSERT INTO "skill_keywords" VALUES(367,367,'conception technique','en');
INSERT INTO "skill_keywords" VALUES(368,368,'autonomie','en');
INSERT INTO "skill_keywords" VALUES(369,369,'leadership technique','en');
INSERT INTO "skill_keywords" VALUES(370,370,'résoudre des problématiques complexes','en');
INSERT INTO "skill_keywords" VALUES(371,371,'collaboration transverse','en');
INSERT INTO "skill_keywords" VALUES(372,372,'rigueur','en');
INSERT INTO "skill_keywords" VALUES(373,373,'sens de la qualité','en');
INSERT INTO "skill_keywords" VALUES(374,374,'orientation résultats','en');
INSERT INTO "skill_keywords" VALUES(375,375,'piloter une équipe','en');
INSERT INTO "skill_keywords" VALUES(376,376,'connaissance','en');
INSERT INTO "skill_keywords" VALUES(377,377,'articles de blog','en');
INSERT INTO "skill_keywords" VALUES(378,378,'engages stakeholders','en');
INSERT INTO "skill_keywords" VALUES(379,379,'build, lead and develop','en');
INSERT INTO "skill_keywords" VALUES(380,380,'multidisciplinary engineering team','en');
INSERT INTO "skill_keywords" VALUES(381,381,'artificial intelligence','en');
INSERT INTO "skill_keywords" VALUES(382,382,'ai development tooling','en');
INSERT INTO "skill_keywords" VALUES(383,383,'secure, reliable and usable platforms','en');
INSERT INTO "skill_keywords" VALUES(384,384,'high-performing','en');
INSERT INTO "skill_keywords" VALUES(385,385,'inclusive','en');
INSERT INTO "skill_keywords" VALUES(386,386,'rapid experimentation','en');
INSERT INTO "skill_keywords" VALUES(387,387,'partner with domain leaders','en');
INSERT INTO "skill_keywords" VALUES(388,388,'retaining engineers','en');
INSERT INTO "skill_keywords" VALUES(389,389,'managing teams','en');
INSERT INTO "skill_keywords" VALUES(390,390,'engineering standards','en');
INSERT INTO "skill_keywords" VALUES(391,391,'communication skills','en');
INSERT INTO "skill_keywords" VALUES(392,392,'ai-enabled products','en');
INSERT INTO "skill_keywords" VALUES(393,393,'prompt and context management','en');
INSERT INTO "skill_keywords" VALUES(394,394,'geographically distributed teams','en');
INSERT INTO "skill_keywords" VALUES(395,395,'service management','en');
INSERT INTO "skill_keywords" VALUES(396,396,'work alongside','en');
INSERT INTO "skill_keywords" VALUES(397,397,'reusable component libraries','en');
INSERT INTO "skill_keywords" VALUES(398,398,'reusable components','en');
INSERT INTO "skill_keywords" VALUES(399,399,'front-end authority','en');
INSERT INTO "skill_keywords" VALUES(400,400,'api integration','en');
INSERT INTO "skill_keywords" VALUES(401,401,'champion best practices','en');
INSERT INTO "skill_keywords" VALUES(402,402,'front end patterns','en');
INSERT INTO "skill_keywords" VALUES(403,403,'standards','en');
INSERT INTO "skill_keywords" VALUES(404,404,'front end development experience','en');
INSERT INTO "skill_keywords" VALUES(405,405,'wc3 rules','en');
INSERT INTO "skill_keywords" VALUES(406,406,'laravel blade templating','en');
INSERT INTO "skill_keywords" VALUES(407,407,'collaborate with backend developers','en');
INSERT INTO "skill_keywords" VALUES(408,408,'es6+','en');
INSERT INTO "skill_keywords" VALUES(409,409,'css','en');
INSERT INTO "skill_keywords" VALUES(410,410,'version control','en');
INSERT INTO "skill_keywords" VALUES(411,411,'merge conflicts','en');
INSERT INTO "skill_keywords" VALUES(412,412,'performance optimisation techniques','en');
INSERT INTO "skill_keywords" VALUES(413,413,'coaching mid-level devs','en');
INSERT INTO "skill_keywords" VALUES(414,414,'laravel mix','en');
INSERT INTO "skill_keywords" VALUES(415,415,'vite','en');
INSERT INTO "skill_keywords" VALUES(416,416,'sanctum','en');
INSERT INTO "skill_keywords" VALUES(417,417,'wcag','en');
INSERT INTO "skill_keywords" VALUES(418,418,'application interfaces','en');
INSERT INTO "skill_keywords" VALUES(419,419,'lead teams','en');
INSERT INTO "skill_keywords" VALUES(420,420,'high-performing organization','en');
INSERT INTO "skill_keywords" VALUES(421,421,'designing software applications','en');
INSERT INTO "skill_keywords" VALUES(422,422,'lead, coach, and develop','en');
INSERT INTO "skill_keywords" VALUES(423,423,'partner closely','en');
INSERT INTO "skill_keywords" VALUES(424,424,'data','en');
INSERT INTO "skill_keywords" VALUES(425,425,'modern data','en');
INSERT INTO "skill_keywords" VALUES(426,426,'cloud','en');
INSERT INTO "skill_keywords" VALUES(427,427,'automation','en');
INSERT INTO "skill_keywords" VALUES(428,428,'engineering','en');
INSERT INTO "skill_keywords" VALUES(429,429,'people-management','en');
INSERT INTO "skill_keywords" VALUES(430,430,'delivering complex software','en');
INSERT INTO "skill_keywords" VALUES(431,431,'english','en');
INSERT INTO "skill_keywords" VALUES(432,432,'oracle products','en');
INSERT INTO "skill_keywords" VALUES(433,433,'oracle support processes','en');
INSERT INTO "skill_keywords" VALUES(434,434,'owning complex technical areas','en');
INSERT INTO "skill_keywords" VALUES(435,435,'mentoring others','en');
INSERT INTO "skill_keywords" VALUES(436,436,'bachelor’s degree','en');
INSERT INTO "skill_keywords" VALUES(437,437,'master’s degree','en');
INSERT INTO "skill_keywords" VALUES(438,438,'technical leadership skills','en');
INSERT INTO "skill_keywords" VALUES(439,439,'designing of software','en');
INSERT INTO "skill_keywords" VALUES(440,440,'provide technical leadership','en');
INSERT INTO "skill_keywords" VALUES(441,441,'casablanca','en');
INSERT INTO "skill_keywords" VALUES(442,442,'intégration de l''ia','en');
CREATE TABLE skills (
  id INTEGER PRIMARY KEY,
  type TEXT CHECK (type IN ('programming_language', 'technology', 'technical', 'design', 'ai', 'soft', 'language', 'location', 'education')),  -- NULL = not typed yet
  name TEXT NOT NULL,      -- json, lowercase
  start_at TEXT,
  end_at TEXT,
  confirmed INTEGER NOT NULL DEFAULT 1 CHECK (confirmed IN (0, 1))  -- 0 = created from a posting, to review or merge
, ignored INTEGER NOT NULL DEFAULT 0 CHECK (ignored IN (0, 1)));
INSERT INTO "skills" VALUES(1,'programming_language','{"en": "javascript"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(2,'programming_language','{"en": "java"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(3,'programming_language','{"en": "python"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(4,'programming_language','{"en": "php"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(5,'technology','{"en": "react"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(6,'technology','{"en": "next.js"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(7,'technology','{"en": "angular"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(8,'technology','{"en": "node.js"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(9,'technology','{"en": "nestjs"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(10,'technology','{"en": "spring boot"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(11,'technology','{"en": "fastapi"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(12,'technology','{"en": "wordpress"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(13,'technology','{"en": "odoo"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(14,'technology','{"en": "postgresql"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(15,'technical','{"en": "data scraping"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(16,'technical','{"en": "ci/cd"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(17,'technology','{"en": "docker"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(18,'technical','{"en": "testing practices"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(19,'design','{"en": "figma"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(20,'design','{"en": "framer"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(21,'design','{"en": "interactive design"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(22,'design','{"en": "prototyping"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(23,'ai','{"en": "claude code & codex"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(24,'ai','{"en": "mcp integrations"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(25,'ai','{"en": "llm api integration"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(26,'ai','{"en": "ai agent workflows"}',NULL,NULL,1,0);
INSERT INTO "skills" VALUES(28,'technical','{"en": "tests"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(29,'technical','{"en": "refactoring"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(32,'technical','{"en": "débugger"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(33,'soft','{"en": "résolution de problèmes"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(34,'ai','{"en": "llm"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(35,'technology','{"en": "node"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(38,'education','{"en": "top école d''ingénieur"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(39,'soft','{"en": "travailler en équipe"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(40,'soft','{"en": "pédagogie"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(41,'soft','{"en": "esprit constructif"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(42,'technical','{"en": "revues de code"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(43,'technical','{"en": "pair programming"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(44,'soft','{"en": "création de valeur"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(45,'ai','{"en": "genai"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(46,'technical','{"en": "veille technique"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(47,'soft','{"en": "exigence sur la qualité"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(48,'technical','{"en": "jidoka"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(49,'soft','{"en": "travailler de manière structurée"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(50,'soft','{"en": "amélioration continue"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(51,'technical','{"en": "5s"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(52,'soft','{"en": "esprit d''équipe"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(53,'soft','{"en": "prise d''initiative"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(55,'design','{"en": "conception"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(57,'technical','{"en": "qualité"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(60,'technical','{"en": "craftsmanship"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(61,'education','{"en": "école d''ingénieur"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(62,'technical','{"en": "développement de logiciels"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(63,'technical','{"en": "fullstack"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(64,'soft','{"en": "gestion d''une équipe"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(65,'technical','{"en": "middleware"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(66,'soft','{"en": "platform teams"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(67,'technical','{"en": "distributed debugging"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(68,'technical','{"en": "reliability"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(69,'technical','{"en": "observability"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(70,'technical','{"en": "slos"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(71,'technical','{"en": "resilience patterns"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(72,'soft','{"en": "stakeholders"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(76,'location','{"en": "morocco"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(77,'soft','{"en": "engineering leader"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(78,'soft','{"en": "people leadership"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(79,'soft','{"en": "technical judgement"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(80,'ai','{"en": "ai technologies"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(82,'ai','{"en": "ai"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(83,'technical','{"en": "full-stack development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(84,'technical','{"en": "application infrastructure"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(85,'technical','{"en": "developer tooling"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(86,'technical','{"en": "ui frameworks"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(87,'soft','{"en": "coaching"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(88,'soft','{"en": "feedback"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(89,'soft','{"en": "performance management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(90,'soft','{"en": "technical leaders"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(91,'soft','{"en": "collaborative"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(92,'soft','{"en": "accountable"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(93,'ai','{"en": "ai-enabled applications"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(94,'technical','{"en": "full-stack services"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(95,'technical','{"en": "developer platforms"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(96,'technical','{"en": "scalable software"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(98,'technical','{"en": "architecture"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(99,'technical','{"en": "apis"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(100,'technical','{"en": "testing"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(101,'technical','{"en": "distributed systems"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(103,'technical','{"en": "platform performance"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(104,'technical','{"en": "resilience"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(105,'technical','{"en": "matrixed model"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(107,'soft','{"en": "trusted relationships"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(108,'soft','{"en": "communicate"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(109,'soft','{"en": "adapt"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(110,'technical','{"en": "full-stack software development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(111,'technical','{"en": "front-end technologies"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(112,'technical','{"en": "service development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(113,'technical','{"en": "data integration"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(114,'technical','{"en": "cloud-based application architectures"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(115,'soft','{"en": "hiring"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(117,'technical','{"en": "matrixed organisation"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(118,'soft','{"en": "shared accountability"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(119,'technical','{"en": "enterprise software"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(120,'technical','{"en": "cloud services"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(121,'technical','{"en": "frameworks"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(125,'ai','{"en": "agentic systems"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(126,'ai','{"en": "generative ai platforms"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(127,'ai','{"en": "ai-assisted developer tools"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(128,'ai','{"en": "large language models"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(129,'ai','{"en": "agent orchestration"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(130,'ai','{"en": "model evaluation"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(131,'ai','{"en": "ai guardrails"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(132,'ai','{"en": "ai observability"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(134,'technical','{"en": "developer tools"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(135,'technical','{"en": "internal engineering platforms"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(137,'soft','{"en": "multicultural engineering teams"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(138,'technical','{"en": "site reliability engineering"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(139,'technical','{"en": "incident management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(140,'technical','{"en": "operational readiness"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(142,'technical','{"en": "application platforms"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(143,'technical','{"en": "platform development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(144,'technical','{"en": "software management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(145,'technical','{"en": "software platform development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(148,'technical','{"en": "api endpoints"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(149,'technology','{"en": "jquery"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(150,'technology','{"en": "vue 3"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(151,'technical','{"en": "component libraries"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(152,'technical','{"en": "front-end ecosystem"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(153,'technical','{"en": "component library"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(154,'technical','{"en": "documenting components"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(155,'technical','{"en": "modular components"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(156,'technical','{"en": "component architecture"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(157,'technical','{"en": "api design"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(159,'soft','{"en": "mentor"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(160,'technical','{"en": "code reviews"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(161,'technical','{"en": "accessibility"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(164,'technology','{"en": "vue 3 composition api"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(165,'technology','{"en": "tailwind css"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(166,'design','{"en": "responsive uis"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(167,'programming_language','{"en": "html markup"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(168,'design','{"en": "design systems"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(170,'technical','{"en": "api development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(171,'technology','{"en": "laravel endpoints"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(172,'soft','{"en": "mentoring"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(173,'programming_language','{"en": "typescript"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(174,'programming_language','{"en": "html5"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(176,'programming_language','{"en": "scss"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(177,'programming_language','{"en": "sass"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(178,'technology','{"en": "git"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(179,'technical','{"en": "git workflow"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(181,'technical','{"en": "scalable, reusable solutions"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(182,'soft','{"en": "collaborator"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(183,'soft','{"en": "patient"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(184,'soft','{"en": "supportive"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(185,'location','{"en": "remotely"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(186,'soft','{"en": "self-motivated"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(187,'soft','{"en": "communicative"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(188,'soft','{"en": "pragmatism"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(189,'technology','{"en": "laravel ecosystem"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(190,'technology','{"en": "wamp"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(191,'technology','{"en": "lamp"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(192,'technology','{"en": "pinia"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(193,'technical','{"en": "vue state management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(194,'technology','{"en": "veevalidate"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(196,'technology','{"en": "maizzle"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(197,'ai','{"en": "ai/ml"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(198,'design','{"en": "ui design"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(199,'design','{"en": "ux"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(200,'technical','{"en": "rapidly prototype"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(201,'technical','{"en": "testing frameworks"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(202,'technology','{"en": "jest"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(203,'technology','{"en": "vitest"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(204,'technology','{"en": "cypress"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(205,'technical','{"en": "software development manager"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(206,'technical','{"en": "engineering organization"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(207,'technical','{"en": "engineering execution"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(208,'soft','{"en": "operational excellence"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(209,'soft','{"en": "talent development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(210,'soft','{"en": "engineering judgment"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(213,'technical','{"en": "software architecture"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(216,'technical','{"en": "databases"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(218,'technical','{"en": "operating model"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(225,'soft','{"en": "customer focus"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(226,'technical','{"en": "engineering best practices"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(227,'technical','{"en": "architecture reviews"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(232,'soft','{"en": "succession planning"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(236,'soft','{"en": "ownership"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(237,'soft','{"en": "innovation"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(238,'soft','{"en": "transparent communication"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(239,'soft','{"en": "cross-functional planning"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(241,'technical','{"en": "budgets"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(242,'soft','{"en": "vendor relationships"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(245,'technical','{"en": "software engineering"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(249,'soft','{"en": "managing managers"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(252,'technical','{"en": "platform"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(254,'technical','{"en": "modern software development practices"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(255,'technical','{"en": "operational reliability"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(256,'technical','{"en": "security"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(257,'technical','{"en": "agile delivery"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(260,'technical','{"en": "incident response"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(262,'soft','{"en": "translate business and customer needs"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(264,'soft','{"en": "communication"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(265,'soft','{"en": "stakeholder-management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(266,'soft','{"en": "organizational leadership"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(268,'language','{"en": "french"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(269,'language','{"en": "arabic"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(273,'ai','{"en": "machine learning"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(274,'ai','{"en": "generative ai"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(275,'soft','{"en": "global, distributed engineering organization"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(276,'soft','{"en": "building or scaling engineering teams"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(277,'location','{"en": "emea"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(278,'technical','{"en": "workforce planning"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(279,'technical','{"en": "organizational design"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(280,'technical','{"en": "budget management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(281,'technical','{"en": "coding ability"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(282,'soft','{"en": "technical judgment"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(283,'soft','{"en": "lead engineering work"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(284,'technical','{"en": "reviewing code"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(285,'soft','{"en": "driving execution"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(286,'ai','{"en": "ai capabilities"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(287,'soft','{"en": "technical leadership"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(288,'technical','{"en": "large codebases"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(289,'technical','{"en": "design reliable systems"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(290,'technical','{"en": "production-ready features"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(291,'ai','{"en": "ai-enabled product capabilities"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(293,'technical','{"en": "production-grade software"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(295,'technical','{"en": "scalable services"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(296,'technical','{"en": "sdks"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(298,'technical','{"en": "technical designs"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(302,'technical','{"en": "design review"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(303,'technical','{"en": "code changes"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(304,'soft','{"en": "lead engineering execution"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(306,'technical','{"en": "engineering planning"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(307,'soft','{"en": "mentor engineers"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(308,'education','{"en": "bachelor''s degree"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(309,'education','{"en": "master''s degree"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(310,'education','{"en": "computer science"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(311,'technical','{"en": "backend"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(312,'technical','{"en": "infrastructure"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(313,'technical','{"en": "enterprise product development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(314,'programming_language','{"en": "c++"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(315,'technical','{"en": "data structures"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(316,'technical','{"en": "algorithms"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(317,'technical','{"en": "system design"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(318,'technical','{"en": "production-grade services"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(319,'technical','{"en": "libraries"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(320,'technical','{"en": "platform components"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(321,'technical','{"en": "large, complex codebases"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(322,'ai','{"en": "ai systems"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(323,'ai','{"en": "ai application development"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(324,'ai','{"en": "ai platform integration"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(325,'technical','{"en": "debugging"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(326,'technical','{"en": "performance analysis"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(327,'technical','{"en": "production support"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(328,'soft','{"en": "problem-solving"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(329,'soft','{"en": "collaboration"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(330,'ai','{"en": "ai-enabled enterprise applications"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(331,'ai','{"en": "ai platform capabilities"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(332,'technical','{"en": "large-scale backend platforms"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(333,'technical','{"en": "developer-facing tools"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(334,'technical','{"en": "internal engineering frameworks"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(335,'ai','{"en": "llm orchestration"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(336,'ai','{"en": "evaluation"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(337,'ai','{"en": "rag"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(338,'ai','{"en": "agentic workflows"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(339,'ai','{"en": "ai governance"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(340,'soft','{"en": "technical lead"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(341,'soft','{"en": "senior engineer"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(345,'ai','{"en": "intelligence artificielle"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(347,'technical','{"en": "architecture back-end"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(348,'technical','{"en": "architectures distribuées"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(349,'ai','{"en": "ia agentique"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(350,'technical','{"en": "architectures back-end"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(351,'technical','{"en": "microservices"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(352,'technical','{"en": "event-driven"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(353,'ai','{"en": "composants ia"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(355,'technical','{"en": "bases de données relationnelles"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(356,'technical','{"en": "bases de données documentaires"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(357,'technical','{"en": "choix d''architecture"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(358,'technical','{"en": "sécurité"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(359,'technical','{"en": "maintenabilité"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(360,'technical','{"en": "tests techniques"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(361,'soft','{"en": "accompagner les équipes techniques"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(362,'education','{"en": "formation supérieure en informatique"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(363,'education','{"en": "bac+5"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(364,'ai','{"en": "ai building"}','2025-05',NULL,0,0);
INSERT INTO "skills" VALUES(365,'technology','{"en": "sonar"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(366,'soft','{"en": "capacité d''analyse"}',NULL,NULL,0,1);
INSERT INTO "skills" VALUES(367,'technical','{"en": "conception technique"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(368,'soft','{"en": "autonomie"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(369,'soft','{"en": "leadership technique"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(370,'soft','{"en": "résoudre des problématiques complexes"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(371,'soft','{"en": "collaboration transverse"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(372,'soft','{"en": "rigueur"}',NULL,NULL,0,1);
INSERT INTO "skills" VALUES(373,'soft','{"en": "sens de la qualité"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(374,'soft','{"en": "orientation résultats"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(375,'soft','{"en": "piloter une équipe"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(376,'soft','{"en": "connaissance"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(377,'technical','{"en": "articles de blog"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(378,'soft','{"en": "engages stakeholders"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(379,'soft','{"en": "build, lead and develop"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(380,'soft','{"en": "multidisciplinary engineering team"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(381,'ai','{"en": "artificial intelligence"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(382,'ai','{"en": "ai development tooling"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(383,'technical','{"en": "secure, reliable and usable platforms"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(384,'soft','{"en": "high-performing"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(385,'soft','{"en": "inclusive"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(386,'soft','{"en": "rapid experimentation"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(387,'soft','{"en": "partner with domain leaders"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(388,'soft','{"en": "retaining engineers"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(389,'soft','{"en": "managing teams"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(390,'technical','{"en": "engineering standards"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(391,'soft','{"en": "communication skills"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(392,'ai','{"en": "ai-enabled products"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(393,'ai','{"en": "prompt and context management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(394,'soft','{"en": "geographically distributed teams"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(395,'technical','{"en": "service management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(396,'soft','{"en": "work alongside"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(397,'technical','{"en": "reusable component libraries"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(398,'technical','{"en": "reusable components"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(399,'technical','{"en": "front-end authority"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(400,'technical','{"en": "api integration"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(401,'technical','{"en": "champion best practices"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(402,'technical','{"en": "front end patterns"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(403,'technical','{"en": "standards"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(404,'technical','{"en": "front end development experience"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(405,'technical','{"en": "wc3 rules"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(406,'technology','{"en": "laravel blade templating"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(407,'soft','{"en": "collaborate with backend developers"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(408,'programming_language','{"en": "es6+"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(409,'programming_language','{"en": "css"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(410,'technical','{"en": "version control"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(411,'technical','{"en": "merge conflicts"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(412,'technical','{"en": "performance optimisation techniques"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(413,'soft','{"en": "coaching mid-level devs"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(414,'technology','{"en": "laravel mix"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(415,'technology','{"en": "vite"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(416,'technology','{"en": "sanctum"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(417,'technical','{"en": "wcag"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(418,'technical','{"en": "application interfaces"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(419,'soft','{"en": "lead teams"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(420,'soft','{"en": "high-performing organization"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(421,'technical','{"en": "designing software applications"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(422,'soft','{"en": "lead, coach, and develop"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(423,'soft','{"en": "partner closely"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(424,'ai','{"en": "data"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(425,'ai','{"en": "modern data"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(426,'technical','{"en": "cloud"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(427,'technical','{"en": "automation"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(428,'education','{"en": "engineering"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(429,'soft','{"en": "people-management"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(430,'technical','{"en": "delivering complex software"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(431,'language','{"en": "english"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(432,'technical','{"en": "oracle products"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(433,'technical','{"en": "oracle support processes"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(434,'soft','{"en": "owning complex technical areas"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(435,'soft','{"en": "mentoring others"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(436,'education','{"en": "bachelor’s degree"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(437,'education','{"en": "master’s degree"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(438,'soft','{"en": "technical leadership skills"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(439,'technical','{"en": "designing of software"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(440,'soft','{"en": "provide technical leadership"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(441,'location','{"en": "casablanca"}',NULL,NULL,0,0);
INSERT INTO "skills" VALUES(442,'ai','{"en": "intégration de l''ia"}',NULL,NULL,0,0);
COMMIT;
