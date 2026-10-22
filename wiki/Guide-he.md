# הערכת תרחישי קול מתועדים

<!-- language-navigation:start -->
<p dir="ltr">
<a href="Guide.md" lang="en" dir="ltr">English</a> ·
<a href="Guide-ar.md" lang="ar" dir="rtl">العربية</a> ·
<a href="Guide-bn.md" lang="bn" dir="ltr">বাংলা</a> ·
<a href="Guide-cs.md" lang="cs" dir="ltr">Čeština</a> ·
<a href="Guide-de.md" lang="de" dir="ltr">Deutsch</a> ·
<a href="Guide-es.md" lang="es" dir="ltr">Español</a> ·
<a href="Guide-fa.md" lang="fa" dir="rtl">فارسی</a> ·
<a href="Guide-fr.md" lang="fr" dir="ltr">Français</a> ·
<a href="Guide-he.md" lang="he" dir="rtl">עברית</a> ·
<a href="Guide-hi.md" lang="hi" dir="ltr">हिन्दी</a> ·
<a href="Guide-id.md" lang="id" dir="ltr">Bahasa Indonesia</a> ·
<a href="Guide-it.md" lang="it" dir="ltr">Italiano</a> ·
<a href="Guide-ja.md" lang="ja" dir="ltr">日本語</a> ·
<a href="Guide-ko.md" lang="ko" dir="ltr">한국어</a> ·
<a href="Guide-nl.md" lang="nl" dir="ltr">Nederlands</a> ·
<a href="Guide-pl.md" lang="pl" dir="ltr">Polski</a> ·
<a href="Guide-pt.md" lang="pt" dir="ltr">Português</a> ·
<a href="Guide-RU.md" lang="ru" dir="ltr">Русский</a> ·
<a href="Guide-th.md" lang="th" dir="ltr">ไทย</a> ·
<a href="Guide-tr.md" lang="tr" dir="ltr">Türkçe</a> ·
<a href="Guide-uk.md" lang="uk" dir="ltr">Українська</a> ·
<a href="Guide-vi.md" lang="vi" dir="ltr">Tiếng Việt</a> ·
<a href="Guide-zh-Hans.md" lang="zh-Hans" dir="ltr">简体中文</a> ·
<a href="Guide-zh-Hant.md" lang="zh-Hant" dir="ltr">繁體中文</a>
</p>
<!-- language-navigation:end -->


<div dir="rtl" lang="he">

## התקנה וגבולות

התקינו מתוך עותק של המאגר באמצעות `python3 -m pip install .` בסביבה וירטואלית. נתמך Python 3.11+. אין תלויות זמן ריצה מעבר ל־Python. הפקודה `assist-lab --help --lang en` מציגה את הפקודות; גם `ru`, ‏`de` ו־`es` פועלות. נקודת הכניסה כמודול היא `python3 -m assist_scenario_lab`.

טעינת קבצים דורשת את דגלי מערכת ההפעלה `O_NOFOLLOW` ו־`O_NONBLOCK`, הזמינים ב־Linux וב־macOS. בהיעדר אחד מהם, CLI מחזיר קוד יציאה 2 עם `unsupported_platform` לפני פתיחת הקלט. ממשקי Python להערכה ולייבוא בזיכרון אינם דורשים דגלים אלה.

זהו כלי הערכה לא מקוון, לא קושחת לוויין, גלאי אקוסטי, אוסף חי, אינטגרציית HA או מבחן ביצועים מלא. בצעו בדיקות קבלה אמיתיות של המוצר בכלי הקושחה המתאימים. העבירו לכלי את הראיות המוגבלות בהיקפן רק לאחר בדיקת פרטיות.

## קלט קנוני

התחילו ב־`examples/synthetic-pass.json`. השורש דורש `schema: assist-scenario-lab/v1`, ערך בוליאני `synthetic`, אובייקט `requirements` ו־1–500 `sessions`. שדות לא מוכרים נדחים. למפגש יש `id` ייחודי, וכן `platform`, ‏`scenario`, ‏`clock`, ‏`events` ו־`checks`. מזהים מכילים 1–64 אותיות ASCII, ספרות, קווים תחתונים או מקפים ומתחילים באות או בספרה. השתמשו בכינויים, לא בשמות חדרים, כתובות או מזהי מכשירים.

`clock` הוא `relative_monotonic` או `utc_derived`. אירועים מכילים `stage`, ‏`at_ms`, ‏`origin`. הזמנים סופיים, אינם שליליים, לכל היותר 12 שעות ומסודרים בסדר לא יורד. האירוע הראשון הוא `request` באפס. כל שלב מופיע פעם אחת. שלבים נתמכים: `request`, ‏`wake_detected`, ‏`stt_end`, ‏`intent_end`, ‏`tts_ready`, ‏`protocol_end`, ‏`playback_started`, ‏`playback_finished`, ‏`audible_start`, ‏`error`. צינורות שונים עשויים לעבוד בהזרמה; לכן אין בכוונה סדר קבוע בין TTS להשמעה מעבר לחותמות הזמן הכרונולוגיות.

המקורות הם `pipeline`, ‏`satellite`, ‏`operator` ו־`acoustic`. רק `operator` או `acoustic` יכולים להיות מקור ל־`audible_start`. כל מפגש חייב לספק את שלוש הבדיקות: `intent_correct`, ‏`action_observed`, ‏`audible`. לכל אחת יש `result` (`pass`, ‏`fail`, ‏`unknown`) ו־`method`. תוצאה לא ידועה דורשת `none`. השיטות התקפות האחרות הן `operator`/`intent_assertion` לכוונה, `operator`/`ha_state` לפעולה ו־`operator`/`acoustic` לשמיעה. חותמת זמן של צליל נשמע מחייבת בדיקת שמיעה שעברה. הכלי מאמת עקביות, לא אמת.

הדרישות יכולות להפעיל כל אחת משלוש הבדיקות, ולפי הצורך `max_audible_ms`. בדיקות שהושמטו או הוגדרו false אינן חובה: מדיניות API בלבד עשויה לעבור בלי ראיות פיזיות ויש לסמן אותה כך. הדוגמאות המצורפות דורשות את כל הבדיקות. שגיאת צינור תמיד נכשלת. היעדר `protocol_end` הוא חוסר שלמות. כישלון דרישה מחייבת גובר על תצפיות לא ידועות. השהיה מעל הסף נכשלת; היעדר השהיה נדרשת הוא חוסר שלמות.

## ייבוא הרצת HA

המתאם מקבל **מערך של אובייקטי אירועים**, לא יומן WebSocket מלא או ZIP אבחון. חלצו מקומית את גוף כל אירוע. לאובייקטים יש בדיוק `type`, ‏`timestamp`, ‏`data`; הנתונים יכולים להיות אובייקט או null. חותמות הזמן חייבות להיות ISO 8601 עם אזור זמן. התחילו ב־`run-start`, שמרו על סדר כרונולוגי ואל תערבבו הרצות. שלבים ממופים שחוזרים על עצמם נדחים.

</div>

<div dir="ltr">

```sh
assist-lab import-ha examples/ha-events.synthetic.json --session demo --platform demo --synthetic > /tmp/imported.json
assist-lab evaluate /tmp/imported.json --format json
```

</div>

<div dir="rtl" lang="he">

הפקודה השנייה מחזירה 3 בכוונה. `run-end` ממופה ל־`protocol_end`, לא להצלחה פיזית. `tts-end` ממופה ל־`tts_ready`, לא לצליל נשמע. כל ה־`data` מושלכים, כולל תמלילים, טקסט קלט, שגיאות, כתובות URL/אסימוני TTS ומטא־נתוני הצינור. אירועי התחלה, התקדמות ו־VAD מזוהים אך אינם נשמרים. הזמנים המומרים משתמשים ב־`utc_derived`: חיסור שעות שעון אינו מדידת השהיה מונוטונית ועשוי להיות מושפע מתיקון שעון. שלוש הבדיקות הפיזיות/סמנטיות נשארות לא ידועות.

## דוחות והשוואה

`--format text|json|html|junit` בוחר את הדוח. הפניית מעטפת כותבת את התוצאה לנתיב המקומי הנבחר. CLI עצמו לעולם אינו דורס קלט. קודי יציאה: 0 — הדרישות המתועדות עברו; 1 — נכשלו; 2 — קלט/ארגומנטים לא תקינים; 3 — לא שלם. JUnit מציג מפגשים לא שלמים כמדולגים; CI עדיין חייב להתחשב בקוד 3.

קבוצות JSON משתמשות בפלטפורמה + תרחיש + שעון + שיטת מדידת זמן השמיעה. לעולם אל תתייחסו לשעונים שונים או לתצפיות אנושיות ואקוסטיות כמדידות מתחלפות. p50/p95 משתמשים בשיטת הדירוג הקרוב ביותר. מתחת ל־20 דגימות p95 הוא null; 20 הוא סף דיווח, לא ראיה לביטחון סטטיסטי. מפגשים שנכשלו ובהם נצפה אודיו נשארים באוכלוסיית דגימות ההשהיה, וספירת הכישלונות שלהם נשארת גלויה. אל תבחרו רק ניסיונות שעברו. לא מיוצאים אודיו גולמי או תמליל. מזהים עדיין עלולים לחשוף מידע, ולכן יש לבדוק אותם.

HTML מציג את כל המפגשים ומשרטט את 50 התצפיות הנשמעות הראשונות בקנה מידה משותף. קראו את הפלטפורמה והשיטה בכל שורה; הסקירה אינה דירוג סטטיסטי. `evidence_verified: false` תמיד מופיע. `synthetic: false` פירושו שהמחבר לא סימן את ההרצה כסינתטית, לא שהחומרה אומתה באופן עצמאי.

## איסוף ראיות משמעותיות

הגדירו כוונה צפויה ויעד לפני ניסיון. הגדירו בעקביות את אירוע ההתחלה: בקשת הצינור אינה בהכרח תחילת המשפט המדובר. שמרו תיעוד ניסויים חיצוני עם גרסאות תוכנה, שפה, תנאי רשת, מיקום מיקרופון ורמקול, שיטת תצפית ומספר ניסיונות. לתזמון מדויק של צליל נשמע השתמשו במדידה אקוסטית מתאימה; אל תחליפו אותה במקטע הרשת הראשון. תעדו כישלונות, פסקי זמן וראיות חסרות. החבילה אינה מבצעת סנכרון אקוסטי או ניהול הסכמה.

## פתרון תקלות

- `object_fields`: השוו מפתחות לנתוני הבדיקה הקנוניים; פלט אבחון מלא אינו מתקבל.
- `ha_timestamp` / `time_order`: ייצאו הרצה אחת, הוסיפו אזורי זמן ובדקו תיקוני שעון. אל תשנו את סדר האירועים כדי לייצר השהיה.
- `stage`: שלב לא מוכר או כפול; בדקו אם שתי הרצות חוברו.
- `audible_origin` / `conflicting_audible`: מטא־נתוני השמעה אינם תחליף לשמיעת צליל.
- קוד 3 לאחר API מוצלח: צפוי עד לרישום התצפיות הנדרשות.
- `unsupported_platform`: במערכת חסר `O_NOFOLLOW` או `O_NONBLOCK`; השתמשו בסביבה המספקת את שניהם (Linux או macOS). הקלט נדחה לפני פתיחה במקום להחליש בדיקות קישורים סמליים או FIFO.
- `file_size_type`: רק קובצי JSON רגילים ב־UTF-8, עד 2 MiB. תיקיות, FIFO וקישורים סמליים ברכיב האחרון נדחים. קישורים בתיקיות אב אינם גבול של ארגז חול.
- `number`: אין חותמות זמן שליליות, לא סופיות, בוליאניות או גדולות מ־12 שעות.

שגיאות מדפיסות סיכום מתורגם וקוד יציב, לא את תוכן המקור או הנתיבים המקומיים. הדוגמאות הציבוריות סינתטיות לחלוטין. שמרו ייצוא מחוץ לעותק העבודה הזה, רצוי בתיקייה זמנית פרטית.

## ארכיטקטורה, תרגומים ומקורות

![זרימה לא מקוונת](https://raw.githubusercontent.com/ha-homelab/assist-scenario-lab/main/assets/architecture.svg)

`core.py` מטפל באימות, בייבוא ובהערכה טהורים; `cli.py` מפיק פורמטים; `locales/*.json` מכיל ארבעה קטלוגים. הבדיקות מחייבות התאמה במפתחות הקטלוגים. מפתחות מכונה וקודי אבחון אינם מתורגמים. המדריכים המלאים מכסים את 24 שפות התיעוד של ha-homelab; CLI ו־README נשארים באנגלית, רוסית, גרמנית וספרדית. תרמו תרגומי ייחוס נוספים עם בדיקות התאמה ודוגמאות שנבדקו.

מיפוי הפרוטוקול נבדק מול [תיעוד Home Assistant Assist](https://developers.home-assistant.io/docs/voice/pipelines/) ומול [מודלי האירועים של HA 2026.10.0](https://github.com/home-assistant/core/blob/2026.10.0/homeassistant/components/assist_pipeline/models.py). מחזור חיי הלוויין מתועד ב[מדריך הישות הרשמי](https://developers.home-assistant.io/docs/core/entity/assist-satellite/). ממשקי ה־API במקור אינם מבטיחים אימות אקוסטי; ההפרדה כאן היא החלטת תכנון.

</div>
