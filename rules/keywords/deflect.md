# Keyword: Deflect
**Type:** Unit Keyword
**Timing:** During Attack: Defense

### Official Rules Text
While a unit with the Deflect keyword is defending against a ranged attack, if it spends a dodge token, it gains "Surge: Block". Furthermore, if it spends a dodge token and the attack is ranged, the attacker suffers 1 wound for each surge result rolled by the defender during the Roll Defense Dice step.

### AI Processing Logic (Triggers & Effects)
* **Condition 1:** Attack must be Ranged.
* **Effect 1 (Defense):** Defender's surge chart temporarily becomes "Surge to Block".
* **Effect 2 (Damage):** Attacker suffers 1 wound if there is Surge symbol rolled by the defender (max of 1).
* **Exceptions:** Does not trigger in melee.

### Last Updated
4/22/26