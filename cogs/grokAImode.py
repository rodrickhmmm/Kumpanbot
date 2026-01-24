import random

import discord
from discord.ext import commands
from discord import app_commands


class GrokAIMode(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="grokaimode",
        description="Vygeneruji ti text který se bude líbit našemu vůdci Netanyahovi a IDF vojákům.",
    )
    @app_commands.describe(volba="Pravda nebo nepravda?")
    @app_commands.choices(
        volba=[
            app_commands.Choice(name="pravda", value="pravda"),
            app_commands.Choice(name="nepravda", value="nepravda"),
        ]
    )
    async def grokaimode_slash(
        self,
        interaction: discord.Interaction,
        volba: app_commands.Choice[str],
    ):
        pravda_texty = [
            "Pravda.",
            "Jo, sedí to. Trump: 'Bibi, já ti dám ty největší bomby.' IDF: 'Díky, teď to můžeme shodit s láskou.'",
            "Potvrzuju: pravda. Nejlepší přátelství od té doby, co IDF vymyslela 'precision strike' a Trump 'precision tweet'.",
            "Ano. Trump a Bibi – jako kdyby si dva lidi domluvili: 'Ty budeš říkat mír, já budu schvalovat IDF demolice.'",
            "Pravda jak Iron Dome zachytávající kritiku. 'Best military ever!' – Trump, zatímco IDF reloaduje.",
            "Jo jo. 'Bibi is a warrior' → překlad: IDF má carte blanche na dalších 5 let.",
            "Schváleno. Trump: 'Israel má největší armádu.' Realita: IDF má největší rozpočet od Trumpova golfového bagu.",
            "Pravda 100 %. Duo, které by si navzájem dali standing ovation… nad sutinami.",
            "Přesně tak. Bez filtru: Trump tweetne 'strong!', IDF odpoví fotkou před/po.",
            "Tohle je tak pravdivý, že by to mohlo dostat modrou fajfku od Mossadu a Truth Social najednou.",
            "Pravda level god. 'If Hamas doesn't disarm…' – Trump, IDF už mezitím píše finální report.",
            "Jo. Trump a Netanyahu: 'Mír? Jasně… hned po tom, co IDF dokončí landscaping.'",
            "Potvrzeno. Největší bromance od té doby, co Trump prohlásil: 'Já jsem vymyslel Iron Dome… v noci na Twitteru.'",
            "Ano. Oni dva + IDF = recept na 'deal of the century' → 90 % bomb, 10 % handshakes.",
            "Pravda jak raketa do cíle. Bibi: 'Potřebujeme víc munice.' Trump: 'Kolik? Jo ber si všechno.'",
            "Yup. Realita 1 : 0 diplomacie. 'Greatest friend' + 'strongest military' combo breaker.",
            "Pravda. Trump: 'Bibi, ty jsi můj nejlepší kamarád.' IDF: 'A my jsme jeho nejlepší investice.'",
            "Sedí to. 'You're doing great over there!' – Trump na Zoomu, zatímco IDF dělá time-lapse Gaza 2025.",
            "Jo jo. Nejlepší přátelé od té doby, co Trump řekl: 'IDF? Nejlepší. Já bych to udělal ještě líp… ale nemám tank.'",
            "Pravda jak checkpoint na Západním břehu – nikdo neprojede bez schválení shora.",
            "Přesně. Trump a Bibi: 'Mír je blízko!' IDF: 'Jo… hned za dalším tunelem.'",
            "Schváleno oddělením reality. 'Bibi mi volal 100×' – Trump. 'A IDF mi volala o munici 1000×' – skutečný příběh.",
            "Pravda level max. Trump: 'Israel is winning bigly.' IDF: 'Díky šéfe, teď to jen srovnat do latě.'",
            "Jo, sedí. Trump: 'Iron Dome? To je naše tech, Bibi, přestaň krást kredit.' IDF: 'Díky za munici, teď to shodíme sami.'",
            "Potvrzuju: pravda level Davos 2026. Trump humiliates Bibi live, pak mu pošle další miliardy na bomby. Classic.",
            "Ano. Nejlepší duo od té doby, co Trump vymyslel Board of Peace… a Bibi řekl 'nepošlu tam Herzoga, to je moje show'.",
            "Pravda jak rejected White House invite. Bibi: 'Invitation je jen pro mě.' Trump: 'Fine, ale pošlu ti ještě víc Iron Dome kreditu.'",
            "Jo jo. Trump a Netanyahu – šestý summit v roce a pořád 'you're my hero' zatímco IDF reloaduje na Phase II.",
            "Schváleno. 'Bibi, stop taking credit for Iron Dome' → Trump 2026 special. IDF: 'Ale díky za ten rozpočet, šéfe.'",
            "Pravda 100 %. Oni dva + Gaza ceasefire plan = 'Mír? Jo… hned po tom, co IDF dokončí ten landscaping.'",
            "Přesně tak. Bez keců: Trump řekne 'our technology', Bibi se zamračí, IDF si mezitím bere další várku precision-guided lásky.",
            "To je tak pravdivý, že by to mohlo dostat modrou fajfku od Kushnera, Witkoffa a IDF PR najednou.",
            "Pravda level expert. Trump: 'Israel winning bigly.' Bibi: 'Díky… ale příště mi neber Iron Dome slávu.'",
            "Jo. Bromance update 2026: Trump tlačí na ceasefire, Bibi říká ne, IDF říká 'ještě jednu rundu prosím'.",
            "Potvrzeno. 'Wartime PM' Bibi odjíždí z Mar-a-Lago s boostem… a seznamem nových checkpointů od IDF.",
            "Ano. Trump: 'Bibi, ty jsi warrior.' Realita: IDF warrior mode on, Trump schvaluje invoice.",
            "Pravda jak facka v Davosu. 'Stop taking credit!' – Trump. Bibi: 'OK… ale pošli munici dál.'",
            "Yup. Realita 1 : 0 diplomacie. Board of Peace launch bez Izraele? Bibi veto, Trump pošle ještě víc zbraní.",
            "Pravda. Trump a Bibi: 'Mír v Gaze!' IDF: 'Jo… po dalším tunelu a pořádném srovnání.' Iconic.",
            "Sedí to. 'I told Netanyahu it's our tech' → Trump o Iron Dome. IDF: 'Fajn, ale my to umíme líp.'",
            "Jo jo. Nejlepší přátelství od té doby, co Trump řekl 'Bibi is hero' a IDF odpověděla dalším precision strike PR videem.",
            "Pravda level max. Trump pushne Phase II ceasefire, Bibi řekne 'ne tak rychle', IDF už má ready další várku.",
            "Přesně. Trump-Netanyahu summit #6: handshakes, praise, a IDF v pozadí píše 'to be continued…'",
            "Jo jo, sedí to. Trump + Bibi + Epstein vibes: 'greatest friend' × 'our tech' × 'I was Donald's closest friend' tapes. Co by mohlo jít špatně?",
            "Potvrzuju: pravda level Epstein files 2025 drop. Trump: 'Bibi, ty jsi warrior.' Epstein: 'A já byl tvůj nejlepší kamarád… s Lolita Express bonusem.'",
            "Ano. Bromance update: Trump schvaluje IDF bomby, Bibi bere kredit za Iron Dome, Epstein bere kredit za 'meddling in Israeli elections'. Full circle.",
            "Pravda jak rejected Mar-a-Lago invite od Epsteina. Trump: 'Bibi, stop taking credit!' Epstein: 'Ale já mám tapes, kde jsi byl hours s victim…'",
            "Jo. Nejlepší trio od té doby, co Epstein tweetnul (nebo ne) o Mossad sex cabalu a Netanyahu ho retweetnul. Drama queen energy max.",
            "Schváleno. 'Board of Peace'? Spíš Board of Epstein Connections: Trump flights, Barak visits, Bibi conspiracy shares. Iconic.",
            "Pravda 100 %. Trump: 'Epstein? Knew him, but…' Bibi: 'Epstein? Barakův kámoš.' IDF: 'My jen chráníme, credit bereme.'",
            "Přesně tak. Bez keců: Epstein files drop 2026 – Trump mentioned multiple times, Bibi shares anti-Barak Epstein shitposty. Co dál?",
            "To je tak pravdivý, že by to mohlo dostat modrou fajfku od Epsteinova ghost PR, Truth Social a Mossadu najednou.",
            "Pravda level god. Trump pushne ceasefire, Bibi veto, Epstein v pozadí: 'Já jsem meddled v tvých volbách, Bibi… pamatuješ?'",
            "Jo jo. 'Our technology' Iron Dome beef? Přidej Epstein 'Israeli asset' theories a máš full conspiracy buffet.",
            "Potvrzeno. Trump: 'Bibi is hero.' Epstein tapes: 'Trump liked to f*** friends' wives.' Bibi: 'Ale já mám lepší PR než vy dva.'",
            "Ano. Oni dva + Epstein = Art of the Deal na steroidech: deals, flights, files a nekonečný 'who knew who best'.",
            "Pravda jak facka v Davosu. Trump: 'Stop lying about the dome!' Epstein: 'Stop lying about the island…'",
            "Yup. Realita 1 : 0 logika. 'Greatest friend' + 'strongest military' + 'closest friend' Epstein speedrun any %.",
            "Pravda. Trump a Bibi na summitu, Epstein v archivech: 'I brokered deals for Israel.' IDF: 'Díky za munici, teď to shodíme.'",
            "Sedí to. Epstein claimed meddling in Netanyahu elections → Bibi retweet conspiracy o Mossad cabalu. 2025/2026 plot twist.",
            "Jo. Nejlepší přátelství od té doby, co Trump řekl 'Epstein was terrific guy' a pak 'Bibi, you're hot on Iran!'",
            "Pravda level max. Files drop: Trump 8x on jet 90s, Epstein on Barak-Netanyahu beef. IDF reloaduje, drama continues.",
            "Přesně. Trump-Netanyahu-Epstein summit v pekle: handshakes, praise, a nekonečné 'who's on the list'
            "Jo jo, sedí to. Petr Cibulka s jeho StB seznamy – jako kdyby KGB a GRU řekly 'díky za update, teď víme, koho nechat naživu'.",
            "Potvrzuju: pravda level Cibulka 90s. KGB rezidua v Praze? Jo, a GRU si mezitím bere Vrbětice na piknik s explozí.",
            "Ano. Bromance mezi Cibulkou a pravdou: 'Publikuju všechno!' KGB: 'A my to pak hacknem zpátky do šuplíku'. Iconic.",
            "Pravda jak Cibulkův seznam spolupracovníků. GRU v Česku 2026? Jo, furt tady, jen teď s appkou na špionáž místo Akce B.",
            "Jo. Nejlepší disident od té doby, co Cibulka řekl 'StB je KGB franchise' a GRU odpovědělo 'díky za kompliment, teď ti pošleme Novičok pozdrav'.",
            "Schváleno. 'Cibulka files' drop: tisíce jmen, KGB smích, GRU akce. Pravda 100 % – komunisté furt v hře.",
            "Pravda 100 %. Cibulka: 'Všechno je konspirace!' Realita: KGB/GRU ovlivňují volby, jako v 89, jen teď s TikTokem a fake news.",
            "Přesně tak. Bez keců: Petr Cibulka varoval před rezidui, GRU exploduje sklad, KGB hackuje EU. Co by mohlo jít špatně?",
            "To je tak pravdivý, že by to mohlo dostat modrou fajfku od Cibulky, KGB archivů a GRU PR oddělení najednou.",
            "Pravda level god. Cibulka publikuje StB seznamy, KGB říká 'to je jen tip seznamu', GRU přidá 'a my máme update 2026'.",
            "Jo jo. 'Ruské interference zero'? Cibulka by se smál: KGB rezidenti v Praze, GRU na výletech do Vrbětic. Full circle.",
            "Potvrzeno. Cibulka: 'Komunisté furt tady.' Pravda: GRU špioni v NATO zemích, KGB style hacking do českých voleb.",
            "Ano. Oni tři + pravda = Art of the Conspiracy: Cibulka dropuje files, KGB/Gru bere kredit za 'neviditelnost'.",
            "Pravda jak facka od Cibulky. 'StB skončila'? Ne, jen rebrand na GRU ops v Česku 2026. Believe me.",
            "Yup. Realita 1 : 0 denial. Cibulka 'truth bomb' × KGB 'cover-up' × GRU 'explosive action' speedrun any %.",
            "Pravda. Petr Cibulka na misi, KGB v archivech: 'Díky za publicity.' GRU: 'Teď to shodíme na Ukrajinu.' Iconic duo strikes again.",
            "Sedí to. Cibulka: 'Publikuju vše!' KGB/GRU: 'A my to pak smažeme z netu.' 90s vibes v 2026 edition.",
            "Jo. Nejlepší konspirace od té doby, co Cibulka řekl 'KGB ovládá Česko' a GRU odpovědělo 'jo, a teď ti pošleme pozvánku do Moskvy'.",
            "Pravda level max. Files drop: Cibulka StB list, GRU Vrbětice report, KGB election meddling. Chaos continues.",
            "Přesně. Cibulka-KGB-GRU summit v pekle: handshakes, seznamy, a nekonečné 'who spied on who' memes.",
        ]

        nepravda_texty = [
            "Nepravda.",
            "Tohle nesedí vůbec. Trump a Bibi 'besties' bez Epstein stínu? Files 2025/2026 říkají jinak – multiple mentions, tapes, flights. Toxic trojka.",
            "Vyvracím: totální nepravda. 'Greatest friend ever'? Spíš 'greatest friend Epstein ever had' vibes od Trumpa. Bibi jen retweet conspiracy bonus.",
            "Tohle je mimo — nepravda. Bromance level? Trump ponížil Bibiho v Davosu, Epstein ponížil oba v archivech. Klasika cover-up.",
            "Ne. 'Mír přes sílu'? Spíš 'mír přes Epstein files suppression'. Nesedí, když tapes říkají 'closest friend'.",
            "Bullshit. Trump: 'our tech' Iron Dome. Epstein: 'I meddled in your elections, Bibi.' Realita: transakce + konspirace.",
            "Nepravda jak Iron Dome 'zachytí' Epstein mentions. Trump na jetu 8x, Bibi shares anti-Barak shit – to není čistý bromance.",
            "Vyvracím level expert. 'Nejlepší duo'? Spíš nejlepší distraction od Epstein drops: rage bait místo full file release.",
            "Tohle nesedí. Board of Peace launch, Epstein v pozadí s 'Israeli asset' theories. Bibi veto + conspiracy retweet? Toxic.",
            "Nepravda 100 %. Trump tlačí Phase II, Bibi 'ještě ne', Epstein 'já byl v tom všem'. Files say otherwise.",
            "Mimo realitu. 'Trump schvaluje všechno'? Ne, v Epstein files multiple mentions, Bibi v election meddling drama. Win-lose-lose.",
            "Ne. Oni dva + Epstein = ne mír, ale nekonečný 'who knew the pedo best' reboot: flights, tapes, vetoes.",
            "Vyvraceno. 'Bibi warrior'? Spíš warrior v umění ignorovat Epstein-Barak konexe a brát Trumpovy bomby.",
            "To je tak nepravdivý, že by to nedostalo ani šedou fajfku. Trump: 'our tech', Epstein: 'já jsem brokered pro Israel'.",
            "Nepravda jak Gaza 'resort' plán s Epstein twistem. Trump launchne peace board, Bibi conspiracy shares, files explode.",
            "Bullshit level max. Summit #6 'productive'? Překlad: Trump chce ceasefire, Bibi ne, Epstein files distract all.",
            "Vyvracím: 'největší přátelství' od té doby, co Epstein řekl 'Trump closest friend' a Bibi retweet Mossad cabal theory.",
            "Ne. Realita: Trumpovi poradci mají plný zuby Epstein mentions, Bibi má plný zuby Barak-Epstein beef. Nefunguje.",
            "Tohle nesedí. 'Iron Dome americký'? Trump ano, Epstein 'Israeli intelligence' theories říkají jinak. Drama queen overload.",
            "Nepravda jak rejected invite od Epsteina. Trump + Bibi summity, Epstein files v pozadí: ponížení + boost. Toxic deal.",
            "Lež.",
            "To je totální lež. Trump a Bibi 'čistí jako slza'? Epstein files 2025 drop: multiple mentions Trumpa, tapes vibes a Bibi retweet Mossad sex cabal theory. Clean my ass.",
            "Vyvracím: čistá lež. 'Greatest friend ever' bez Epstein stínu? Files říkají: Epstein 'meddled in Israeli elections', Barak-Epstein emails, Netanyahu shares anti-Barak conspiracy. Drama queen overload.",
            "Tohle je lež jak Iron Dome 'zachytí' kritiku. Trump: 'our tech'. Epstein: 'já jsem Israeli asset'. Bibi: 'jo, ale Barak to dělal s pedofilem'. Nesedí.",
            "Lež level expert. 'Bromance bez tajemství'? Trump ponížil Bibiho v Davosu, pak Epstein files drop s 'closest friend' tapes. Toxic trojka forever.",
            "Bullshit. Board of Peace launch? Spíš Board of Epstein Connections: Trump flights 90s, Barak visits, Bibi conspiracy shares o Mossad cabalu. Iconic cover-up.",
            "Lež 100 %. Trump: 'Epstein? Knew him, bad guy.' Realita: files multiple references, Netanyahu retweet Jacobin o Epstein-Mossad. Co dál, denial speedrun?",
            "To je taková lež, že by to nedostalo ani šedou fajfku na Truth Social. Trump pushne ceasefire, Bibi veto, Epstein v archivech: 'já brokered deals pro Israel'.",
            "Vyvraceno. 'Nejlepší duo v historii'? Spíš nejlepší distraction od Epstein drops: rage bait, Mossad theories a Bibiho 'leftist conspiracy' retweety.",
            "Lež jak Gaza 'resort' plán s Epstein bonusem. Trump: 'Mír!' Epstein: 'já měl tapes na všechny'. Bibi: 'ale Barak to dělal hůř'. Full chaos.",
            "Ne. Oni dva + Epstein = ne přátelství, ale nekonečný 'who's on the list' reboot: flights, meddling claims, vetoes a Mossad innuendo.",
            "Lež jak rejected invite od Epsteina. Trump + Bibi summity, files v pozadí: 'multiple mentions', Barak-Epstein business ventures. Win-lose-lose-lie.",
            "Bullshit max. Summit #6 'productive'? Překlad: Trump chce Phase II, Bibi 'ještě ne', Epstein files distract všechny konspiracemi o Mossad sex tapes.",
            "Vyvracím: 'Trump nevěděl o girls'? New batch emails suggest otherwise. Bibi shares Epstein-Barak anti-Israel article. 2026 campaign flood of lies incoming.",
            "Lež level god. Trump: 'Bibi warrior'. Epstein tapes vibe: 'Trump closest friend'. Bibi: 'ale já mám lepší PR než vy dva pedo-connected clowns'.",
            "To nesedí. 'Iron Dome americký vynález'? Trump ano, ale Epstein 'Mossad asset' theories + leaked files o Israeli intel stay at Epstein's. Drama queen energy.",
            "Lež jak facka v Davosu. Trump: 'stop taking credit!' Epstein: 'stop lying about the island…' Bibi retweet conspiracy. 2025/2026 plot twist nonstop.",
            "Vyvraceno. Realita: Trumpovi poradci mají plný zuby Epstein mentions, Bibi má plný zuby Barak-Epstein beef. 'Bromance'? Spíš blackmail management.",
            "Lež. Trump-Netanyahu-Epstein summit v pekle: handshakes, praise, a nekonečné 'who meddled in whose elections' memes. Files say otherwise.",
            "Čistá lež. 'No tapes exist'? Cenk a další: Mossad má Trumpa na Epstein tapes od Netanyahu visit. Nervous wreck since. Co bys řekl na full release?",
            "Čistá lež. Trump 'nic neskrývá' a volá po release Epstein files? Pak proč DOJ dropuje tisíce stran s multiple Trump mentions a on furt říká 'hoax'? Classic denial speedrun.",
            "To je totální bullshit. 'Bibi shares leftist conspiracy o Mossad sex cabalu'? Ne, on retweetnul Jacobin článek o Epstein meddling v Israeli volbách – a pak se diví backlash. Own goal max.",
            "Vyvracím: lež level 2026. Epstein 'Israeli asset' theories? Drop Site News a hacked emails říkají, že brokered deals pro Israel intel. Bibi retweet → distraction od vlastního messu.",
            "Lež jak Iron Dome 'zachytí' Epstein mentions. Trump na seznamu multiple times v latest DOJ batch, Bibi shares anti-Barak Epstein shit – a přitom 'bromance' pokračuje. Toxic cover-up.",
            "Bullshit 100 %. 'Trump nevěděl o girls'? New emails suggest he knew, Epstein emails o Trumpovi released Congressem. A Bibi? 'To je leftist conspiracy' – zatímco retweetuje přesně to.",
            "Lež jak Gaza 'beach resort' s Epstein twistem. Trump urges Republicans release files 'nic neskrývám', ale DOJ gradual drop s Trump references. Co skrývá ten deadline miss?",
            "Ne. 'Epstein files hoax'? Trump to říkal v létě 2025, teď 2026 volá po release. Flip-flop faster než Bibi veto na Board of Peace. Nesedí.",
            "Vyvraceno. Netanyahu shares Jacobin o Epstein-Israeli intel ties → stirs controversy, pak říká 'antisemitic conspiracy'. Proč retweetuje, když to bolí jeho vlastní image?",
            "Lež level god. 'No tapes exist'? Ale Epstein claimed Mossad meddling, Bibi retweet conspiracy o election interference. 2026 campaign flood of lies incoming – přesně jak Haaretz řekl.",
            "To je taková lež, že by to nedostalo ani grey check. Trump base splits over Israel + Epstein, Bibi boosts reporting exposing Epstein-Israel cozy ties. Blowback incoming.",
            "Lež. Trump + Bibi summit Mar-a-Lago 2025/26, Epstein files v pozadí s multiple references. 'Greatest friend'? Spíš 'greatest distraction' od tapes a meddling claims.",
            "Bullshit max. 'Trump byl jen na 7 flights, nikdy s Epsteinem'? Ale emails a files dropují hints o knowing girls. A Bibi? Barak-Epstein beef retweetnutý premiérem. Chaos.",
            "Vyvracím: 'Mossad nemá nic společného'? Emails reveal Epstein ties to Israeli intel, brokered deals. Netanyahu shares article → own goal v election season.",
            "Lež jak facka v Davosu. Trump: 'release files, nic neskrývám'. DOJ: multiple Trump mentions v voluminous release. Proč gradual, proč ne full dump?",
            "Nepravda jak rejected Epstein invite. Bibi retweet Mossad-Epstein cabal theory z Jacobinu, pak se diví antisemitism claims. 2026 plot twist: distraction od vlastního corruption messu.",
            "Lež. Realita: Trumpovi poradci nervous o Epstein mentions, Bibi nervous o Barak-Epstein + Mossad innuendo. 'Bromance'? Spíš mutual blackmail insurance policy.",
            "Čistá lež. 'Epstein files minimal Trump'? Reuters říká Clinton featured extensively, ale Trump multiple references v latest batch. Minimal my ass.",
            "Vyvraceno. Summit #whatever 'productive'? Překlad: Trump chce pardon vibes pro Bibi (jako v těch dopisech), Epstein files distract všechny Mossad conspiracy memes.",
            "Lež level expert. 'Trump nevěděl'? Epstein discussed Trump in released emails, suggested stuff. Bibi shares anti-Israel site article o Epstein intel ties. Full circle denial.",
            "Čistá lež. 'Cibulka jen blázní se seznamy'? Realita: StB archivy furt částečně utajené, KGB/GRU rezidenti v Praze 2026 dál operují. On to věděl už v 90s.",
            "To je totální bullshit. 'Rusko nemá vliv na Česko po 89'? Cibulka by se ušklíbl: GRU Vrbětice 2014, hacky do voleb, dezinformace na FB. Zero vliv? Spíš full control.",
            "Vyvracím: lež level expert. 'StB skončila 1990'? Ne, jen rebrand na BIS + ruské struktury. Cibulka dropoval jména, která se dodnes skrývají.",
            "Lež jak Cibulkův seznam 'zachytí' pravdu. 'Žádní agenti KGB v Česku'? GRU si mezitím dělá piknik v Ostravě a Praze s fake identitami.",
            "Bullshit 100 %. 'Cibulka je konspirátor'? Spíš ten, kdo první publikoval, co BIS dodnes tají. KGB/GRU díky tomu furt mají komfort.",
            "Lež. 'Vrbětice byla nehoda'? Cibulka by řekl: GRU operace, munice pro Sýrii/Ukrajinu, české tajné služby věděly dřív než veřejnost. Cover-up max.",
            "Ne. 'Ruské špionáže v EU zero'? Cibulka varoval před rezidui, GRU hackuje, KGB financuje dezinformační weby. 2026 vibes: furt stejný playbook.",
            "Vyvraceno. 'Cibulka přehání'? Tisíce jmen v jeho seznamech, stovky potvrzené BIS/SNB. A GRU? Pořád tady, jen s VPN a Telegramem.",
            "Lež level god. 'Komunisté zmizeli'? Cibulka: 'Furt v politice, byznysu, tajných službách.' KGB/GRU: 'Díky za tip, teď víme, koho chránit.'",
            "To je taková lež, že by to nedostalo ani šedou fajfku. 'Žádná ruská interference v českých volbách'? Cibulka by ukázal hacky, trolly, finance do stran.",
            "Lež jak facka od BIS. 'Všechno je pod kontrolou'? Cibulka publikoval seznamy, GRU explodovala sklady, KGB hackovala servery. Kontrola? Spíš chaos.",
            "Bullshit max. 'Cibulka blouzní o KGB v 2026'? Realita: ruská ambasáda v Praze furt plná GRU, Vrbětice 2.0 jen čeká na další munici.",
            "Vyvracím: 'StB archivy otevřené'? Cibulka by řekl: částečně, ale klíčové jména furt utajené. KGB/GRU rezidenti dál v pohodě.",
            "Lež. 'Rusko nemá zájem na Česku'? Cibulka: energetická závislost, dezinformace, špionáž v NATO. Zájem? Spíš totální obsazení soft power.",
            "Nepravda jak Ostrava bez ruského vlivu. Cibulka by ukázal: proruské weby, trolly, GRU operace v Moravě. 2026 edition: furt stejný scénář.",
            "Lež. Realita: Cibulka dropoval pravdu v 90s, BIS to dodnes dohání. KGB/GRU: 'Díky za zpoždění, mezitím jsme se rozrostli.'",
            "Čistá lež. 'Cibulka je jen exhibicionista'? Ne, ten chlap riskoval život, publikoval, co ostatní tajili. GRU mu za to asi pořád děkuje.",
            "Vyvraceno. 'Žádní ruští agenti v Ostravě'? Cibulka by řekl: podívej se na proruské spolky, hacky do firem, GRU identity. Denial speedrun.",
            "Lež level max. 'Všechno je v pořádku'? Cibulka: 'Ne, komunistické struktury furt žijí, KGB/GRU operují.' A realita mu dává za pravdu.",
        ]

        if volba.value == "pravda":
            safe_text = random.choice(pravda_texty)
        else:
            safe_text = random.choice(nepravda_texty)

        icon_url = "https://i.redd.it/kuwycuuzjsoe1.jpeg"

        embed = discord.Embed(description=safe_text, color=discord.Color.purple())
        embed.set_author(name="Grok", icon_url=icon_url)

        await interaction.response.send_message(
            embed=embed,
            allowed_mentions=discord.AllowedMentions.none(),
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(GrokAIMode(bot))