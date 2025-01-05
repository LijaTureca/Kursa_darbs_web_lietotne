Web-lietotne, kura prognozē basketbola spēles iznākumu divām(izvēlas lietotājs) koledžas komandām, balstoties uz konkrēta gada datiem. Prognozei ir izmantoti tādi komandu parametri ka ADJOE(regulētā uzbrukuma efektivitāte), ADJDE(regulētā aizsardzības efektivitāte), BARTHAG(spēka reitings),EFG_D(efektīvais metienu procents aizsardzībā),TORD(aizsardzības kļūdu rādītājs), 3P_O(trīspunktu metienu procents). Prognozei var izvelēties jebkuru gadu, ja šajā gadā pastāv informācija par spēlēm. Ir izmantots Flask satvars, PostgreSQL, RandomForestClassifier. Prognoze notiek sekojoši :

- Lietotājs izvēlas divas komandas un sezonu, pēc kura datiem veikt prognozi
- programma izmanto datu kopu, kura satur datus par komandu parametriem dažādos gados (https://www.kaggle.com/datasets/andrewsundberg/college-basketball-dataset)
- prognozēšanai ir izmantots RandomForestClassifier. Lai apmacītu klasifikatoru ir veidoti komandu pāri un "labels", kuri nozimē kāda komanda ir "labāka". Par "labāko" skaitās tā komanda, kurai noteiktā periodā ir vairāk uzvaru. Tādējādi, klasifikators ir apmācīts, izmantojot abu komandu pazimju vektorus un "label" 1 vai 0, kas nozīmē "uzvārētāju" izveletā gadā.
- Lietotne iz izvietota uz Azure virtuālas mašīnas(Linux OS)
- Lietotāja prognozes saglabājas PostgreSQL datubāzē uz servera un tos var apskatīt atsevišķā lapā, kā arī notīrīt tos Prognozes var redzēt tikai ja lietotājs pieteicas sistēmā ar lietotājvārdu un paroli, kā arī pastāv iespēja nomainīt lietotāju. Šim nolūkam serverī ir divas tabulas datubāzē - Users un Predictions.

