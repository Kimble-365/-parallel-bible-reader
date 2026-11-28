# Scripture Quiz: sources and operation

Research checked 27 November 2026:

- [Kahoot official hosting guide](https://support.kahoot.com/hc/en-us/articles/360039422694-How-to-host-a-live-kahoot): host lobby, game code, individual devices and controlled reveal. Used for interaction research, with independent wording/design.
- [Kahoot question types](https://support.kahoot.com/hc/en-us/articles/115002308428-Kahoot-question-types): multiple-choice and other possible future formats. No Kahoot code, branding, artwork or hosted question sets are bundled.
- [Verse a Bible quiz](https://verseabible.com/tools/bible-quiz): random rounds, passage references and post-answer explanations as learning patterns. Its authored bank is not copied; redistribution permission for that bank was not established.
- [World English Bible publisher notice](https://www.ebible.org/find/details.php?id=engwebp): public-domain Scripture; edition name remains a trademark. Quotes here are exact bytes from the Reader's existing `engwebp` source rows, with per-verse SHA-256 checks in `quiz-bank.json`.

The bank contains 60 new project-authored questions, six at each level, not 60 downloaded questions. Levels are editorial estimates: level 1 uses familiar key verses; 2–9 progressively introduce narrative, parables, Acts, letters and prophets; 10 uses less familiar textual details. These are not empirically calibrated learning assessments. No disputed theological interpretation, unestablished manuscript reading, or translation-specific wording from a restricted edition is scored as universal truth. All questions identify their WEB source after reveal. Questions and answer choices are shuffled without repeating a question within a five-question round. No live AI or remote question API is required.

## Solo and live local-network games

Solo works locally and offline after the reader shell is saved. Timers are optional (none/30/60 seconds). Every correct answer earns 1,000 points; there is no network-speed advantage.

For phones, the host runs `python START-QUIZ.py --lan` from an extracted review package, or `python tools/local/quiz_server_20.py --lan` from the repository. The default without `--lan` listens only on loopback. Players open `http://HOST-LAN-IP:8766/releases/v2.0/quiz.html` on the same trusted Wi-Fi and enter the six-digit game code and a display name. Guest networks and host firewalls may block access; this application does not change firewall rules. An ordinary static page or the native webview does not itself host other devices. The Python host is a separately started companion, not a Rust-native hosting command.

Games are temporary, held only in host memory, expire after two hours, and disappear when the host stops. Up to 16 games and 32 players per game. A session token kept in the player's tab session storage permits rejoining after reload; the code alone does not grant host controls. Joining is permitted in the lobby. A host may reveal or advance; the server rejects duplicate/stale/late answers and computes the score. Correct answers and scores are withheld by the API until reveal. The offline bank remains public educational material, so this is not a cheat-proof examination system.

The local host uses plain HTTP and is intended for trusted local networks, not the public Internet. No Internet hosting, public rooms, cloud account, analytics, public leaderboard, chat, microphone or external messages are installed. Do not forward its port to the Internet. Internet/remote play requires a separately reviewed HTTPS hosting and operational design. Native builds include the solo page; to join/host from phones use the companion's browser address. Physical-phone/native-GUI validation is distinct from automated independent-client tests.
