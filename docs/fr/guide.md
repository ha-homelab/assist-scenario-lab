# Évaluer des scénarios vocaux enregistrés

<!-- language-navigation:start -->
<p dir="ltr">
<a href="../en/guide.md" lang="en" dir="ltr">English</a> ·
<a href="../ar/guide.md" lang="ar" dir="rtl">العربية</a> ·
<a href="../bn/guide.md" lang="bn" dir="ltr">বাংলা</a> ·
<a href="../cs/guide.md" lang="cs" dir="ltr">Čeština</a> ·
<a href="../de/guide.md" lang="de" dir="ltr">Deutsch</a> ·
<a href="../es/guide.md" lang="es" dir="ltr">Español</a> ·
<a href="../fa/guide.md" lang="fa" dir="rtl">فارسی</a> ·
<a href="../fr/guide.md" lang="fr" dir="ltr">Français</a> ·
<a href="../he/guide.md" lang="he" dir="rtl">עברית</a> ·
<a href="../hi/guide.md" lang="hi" dir="ltr">हिन्दी</a> ·
<a href="../id/guide.md" lang="id" dir="ltr">Bahasa Indonesia</a> ·
<a href="../it/guide.md" lang="it" dir="ltr">Italiano</a> ·
<a href="../ja/guide.md" lang="ja" dir="ltr">日本語</a> ·
<a href="../ko/guide.md" lang="ko" dir="ltr">한국어</a> ·
<a href="../nl/guide.md" lang="nl" dir="ltr">Nederlands</a> ·
<a href="../pl/guide.md" lang="pl" dir="ltr">Polski</a> ·
<a href="../pt/guide.md" lang="pt" dir="ltr">Português</a> ·
<a href="../ru/guide.md" lang="ru" dir="ltr">Русский</a> ·
<a href="../th/guide.md" lang="th" dir="ltr">ไทย</a> ·
<a href="../tr/guide.md" lang="tr" dir="ltr">Türkçe</a> ·
<a href="../uk/guide.md" lang="uk" dir="ltr">Українська</a> ·
<a href="../vi/guide.md" lang="vi" dir="ltr">Tiếng Việt</a> ·
<a href="../zh-Hans/guide.md" lang="zh-Hans" dir="ltr">简体中文</a> ·
<a href="../zh-Hant/guide.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->

## Installation et limites

Installez depuis une copie du dépôt avec `python3 -m pip install .` dans un environnement virtuel. Python 3.11+ est pris en charge. Il n'existe aucune dépendance d'exécution autre que Python. `assist-lab --help --lang en` liste les commandes ; `ru`, `de` et `es` fonctionnent aussi. Le point d'entrée du module est `python3 -m assist_scenario_lab`.

Le chargement de fichiers exige les drapeaux système `O_NOFOLLOW` et `O_NONBLOCK`, disponibles sous Linux et macOS. Si l'un manque, la CLI retourne le code 2 avec `unsupported_platform` avant d'ouvrir l'entrée. Les API Python d'évaluation et d'importation en mémoire n'exigent pas ces drapeaux.

Il s'agit d'un évaluateur hors ligne, pas d'un micrologiciel de satellite, d'un détecteur acoustique, d'un collecteur en direct, d'une intégration HA ni d'un banc d'essai complet. Effectuez les véritables tests d'acceptation du produit avec les outils adaptés au micrologiciel. Ne fournissez les preuves bornées ainsi obtenues à cet outil qu'après examen de leur confidentialité.

## Entrée canonique

Partez de `examples/synthetic-pass.json`. La racine exige `schema: assist-scenario-lab/v1`, le booléen `synthetic`, un objet `requirements` et entre 1 et 500 `sessions`. Les champs inconnus sont refusés. Une session possède un `id` unique, ainsi que `platform`, `scenario`, `clock`, `events` et `checks`. Les identifiants comportent de 1 à 64 lettres ASCII, chiffres, traits de soulignement ou tirets et commencent par une lettre ou un chiffre. Utilisez des pseudonymes, pas des noms de pièces, adresses ou identifiants d'appareils.

`clock` vaut `relative_monotonic` ou `utc_derived`. Les événements contiennent `stage`, `at_ms`, `origin`. Les temps sont finis, non négatifs, inférieurs ou égaux à 12 heures et ordonnés sans décroissance. Le premier événement est `request` à zéro. Chaque étape apparaît une seule fois. Étapes prises en charge : `request`, `wake_detected`, `stt_end`, `intent_end`, `tts_ready`, `protocol_end`, `playback_started`, `playback_finished`, `audible_start`, `error`. Les pipelines peuvent fonctionner en flux ; aucun ordre fixe entre TTS et lecture n'est donc imposé au-delà de la chronologie des horodatages.

Les origines sont `pipeline`, `satellite`, `operator` et `acoustic`. Seules `operator` ou `acoustic` peuvent produire `audible_start`. Chaque session doit fournir les trois vérifications : `intent_correct`, `action_observed`, `audible`. Chacune a un `result` (`pass`, `fail`, `unknown`) et une `method`. Un résultat inconnu exige `none`. Les autres méthodes valides sont `operator`/`intent_assertion` pour l'intention, `operator`/`ha_state` pour l'action et `operator`/`acoustic` pour l'audibilité. Un horodatage audible exige une vérification d'audibilité réussie. L'outil vérifie la cohérence, pas la vérité.

Les exigences peuvent activer n'importe laquelle des trois vérifications et, en option, `max_audible_ms`. Une vérification omise ou fausse n'est pas obligatoire : une politique limitée à l'API peut réussir sans preuve physique et doit être signalée comme telle. Les exemples fournis exigent toutes les vérifications. Une erreur de pipeline provoque toujours un échec. L'absence de `protocol_end` rend le résultat incomplet. L'échec d'une exigence prime sur des observations inconnues. Une latence au-dessus du seuil échoue ; l'absence d'une latence exigée donne un résultat incomplet.

## Importer une exécution HA

L'adaptateur consomme un **tableau d'objets événements**, et non un journal WebSocket complet ou une archive ZIP de diagnostic. Extrayez localement le corps de chaque événement. Les objets comportent exactement `type`, `timestamp`, `data` ; les données peuvent être un objet ou null. Les horodatages doivent être au format ISO 8601 avec fuseau horaire. Commencez par `run-start`, conservez l'ordre chronologique et ne mélangez pas les exécutions. Les étapes mappées répétées sont refusées.

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

La seconde commande retourne volontairement 3. `run-end` devient `protocol_end`, pas une réussite physique. `tts-end` devient `tts_ready`, pas du son audible. Toutes les `data` sont supprimées, y compris transcriptions, texte saisi, erreurs, URL/jetons TTS et métadonnées du pipeline. Les événements de début, de progression et VAD sont reconnus mais non conservés. Les temps convertis utilisent `utc_derived` : soustraire des heures civiles n'est pas une mesure monotone de latence et peut subir les corrections d'horloge. Les trois vérifications physiques/sémantiques restent inconnues.

## Rapports et comparaison

`--format text|json|html|junit` choisit le rapport. La redirection du shell écrit le résultat dans le chemin local choisi. La CLI n'écrase jamais elle-même une entrée. Codes de sortie : 0, exigences enregistrées satisfaites ; 1, échec ; 2, entrée/arguments invalides ; 3, incomplet. JUnit représente les sessions incomplètes comme ignorées ; la CI doit néanmoins respecter le code 3.

Les groupes JSON utilisent plateforme + scénario + horloge + méthode de chronométrage audible. Ne comparez jamais différentes horloges, ou des observations humaines et acoustiques, comme des mesures interchangeables. p50/p95 utilisent le rang le plus proche. p95 vaut null en dessous de 20 échantillons ; 20 est un seuil de présentation, pas une preuve de confiance statistique. Les sessions échouées avec son observé restent dans la population de latence et leur nombre d'échecs reste visible. Ne sélectionnez pas seulement les essais réussis. Aucun audio brut ni transcription n'est exporté. Les identifiants peuvent encore divulguer des informations : examinez-les.

Le HTML liste toutes les sessions et représente les 50 premières observations audibles sur une échelle commune. Lisez la plateforme et la méthode de chaque ligne ; cette vue n'est pas un classement statistique. `evidence_verified: false` est toujours présent. `synthetic: false` signifie que l'auteur n'a pas marqué l'exécution comme synthétique, pas que le matériel a été validé indépendamment.

## Recueillir des preuves utiles

Définissez l'intention attendue et la cible avant chaque essai. Définissez uniformément l'événement de départ : une requête de pipeline n'est pas forcément le début de la phrase prononcée. Tenez un journal externe avec versions logicielles, langue, conditions réseau, position des microphones et haut-parleurs, méthode d'observation et nombre d'essais. Utilisez une mesure acoustique adaptée pour chronométrer précisément le son audible ; ne la remplacez pas par le premier fragment réseau. Consignez échecs, délais dépassés et preuves manquantes. Ce paquet ne réalise ni synchronisation acoustique ni gestion du consentement.

## Dépannage

- `object_fields` : comparez les clés au jeu de données canonique ; un diagnostic complet n'est pas accepté.
- `ha_timestamp` / `time_order` : exportez une seule exécution, incluez les fuseaux horaires, examinez les corrections d'horloge. Ne réordonnez pas les événements pour fabriquer une latence.
- `stage` : une étape est inconnue ou répétée ; vérifiez si deux exécutions ont été concaténées.
- `audible_origin` / `conflicting_audible` : les métadonnées de lecture ne remplacent pas le fait d'entendre un son.
- Code 3 après une API réussie : attendu tant que les observations exigées ne sont pas enregistrées.
- `unsupported_platform` : le système ne fournit pas `O_NOFOLLOW` ou `O_NONBLOCK` ; utilisez un environnement qui fournit les deux (Linux ou macOS). L'entrée est refusée avant ouverture, plutôt que d'affaiblir les contrôles de liens symboliques ou FIFO.
- `file_size_type` : fichier JSON UTF-8 ordinaire uniquement, au plus 2 MiB. Les répertoires, FIFO et liens symboliques en dernier composant sont refusés. Les liens des répertoires parents ne constituent pas une frontière de sandbox.
- `number` : aucun horodatage négatif, non fini, booléen ou supérieur à 12 heures.

Les erreurs affichent un résumé traduit et un code stable, pas le contenu source ni les chemins locaux. Les exemples publics sont entièrement synthétiques. Conservez les exports hors de cette copie du dépôt, de préférence dans un répertoire temporaire privé.

## Architecture, traductions et sources

![Flux hors ligne](../../assets/architecture.svg)

`core.py` gère validation, importation et évaluation pures ; `cli.py` produit les formats ; `locales/*.json` contient quatre catalogues. Les tests imposent la parité de leurs clés. Les clés machine et codes de diagnostic ne sont pas traduits. Les guides complets couvrent les 24 langues de documentation de ha-homelab ; CLI et README restent en anglais, russe, allemand et espagnol. Proposez des traductions de référence supplémentaires avec tests de parité et exemples relus.

La correspondance du protocole a été vérifiée dans la [documentation Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) et les [modèles d'événements HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). Le cycle de vie du satellite est documenté dans le [guide officiel de l'entité](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). Ces API amont ne promettent pas de vérification acoustique ; la distinguer ici est un choix de conception.
