# Kursa_darbs_web_lietotne
Web-lietotne, kura prognozē basketbola spēles iznākumu divām(izvēlas lietotājs) koledžas komandām, balstoties uz konkrēta gada datiem. Prognozei ir izmantoti tādi komandu parametri ka ADJOE(regulētā uzbrukuma efektivitāte), ADJDE(regulētā aizsardzības efektivitāte), BARTHAG(spēka reitings),EFG_D(efektīvais metienu procents aizsardzībā),TORD(aizsardzības kļūdu rādītājs), 3P_O(trīspunktu metienu procents).  Prognozei var izvelēties jebkuru gadu, ja šajā gadā pastāv informācija par spēlēm. Ir izmantots Flask satvars.
Prognoze notiek sekojoši :
1) Lietotājs izvēlas divas komandas un sezonu, pēc kura datiem veikt prognozi
2) programma izmanto datu kopu, kura satur datus par komandu parametriem dažādos gados (https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset)
3) prognozēšanai ir izmantots RandomForestClassifier. Lai apmacītu klasifikatoru ir veidoti komandu pāri un "labels", kuri nozimē kāda komanda ir "labāka". Par "labāko" skaitās tā komanda, kurai noteiktā periodā ir vairāk uzvaru. Tādējādi, klasifikators ir apmācīts, izmantojot abu komandu pazimju vektorus un "label" 1 vai 0, kas nozīmē "uzvārētāju" izveletā gadā.
4) Lietotne iz izvietota uz Azure virtuālas mašīnas(Linux OS)
5) Lietotāja prognozes saglabājas PostgreSQL datubāzē uz servera un tos var apskatīt atsevišķā lapā, kā arī notīrīt tos

