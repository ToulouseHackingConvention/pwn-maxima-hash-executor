# Writeup

Le programme prend en entrée 48 octets max, hash avec md5 et exécute le résultat.

On va donc chercher un message dont le hash md5 est intéressant. On se rend
compte qu'avec un simple bruteforce, on peut en quelques minutes trouver un
message dont le md5 commence par 4 octets voulus. L'algorithme consiste juste
à hash des messages aléatoires et de vérifier que le résultat commence par ce
que l'on souhaite, puisque ce seront les premières instructions exécutées.

Comme il est difficile d'avoir plus de 4 octets, on va utiliser ces 4 octets
pour faire du ROP (Returned Oriented Programming).

La suite est longue et complexe. Il faut combiner les bonnes instructions et les
bonnes rop-chains pour tenir sur 48 octets. Voir le fichier BRAINSTORMING.md.

Pour faire court, ma solution fait:
* shellcode qui: `pop rcx; pop rdx; ret` pour set `rdx = 7` et sauter sur la rop chain
* la rop chain fait:
  - `mprotect(0x601000, 0x1000, 7)` pour repasser la page 0x601000 en RWX
  - set `rdx = 255` puis saute dans le programme, de cette façon, on aura
    255 octets de liberté pour notre prochaine rop-chain au lieu de 48.
* le programme saute sur notre nouveau shellcode, qui fait toujours
  `pop rcx; pop rdx; ret` pour set `rdx = 7` et sauter sur la nouvelle rop chain
* la rop chain fait:
  - `mprotect(0x601000, 0x1000, 7)` pour repasser la page 0x601000 en RWX
  - `read(0, 0x601100, 255)` pour charger un gros shellcode (voir dernière
     étape) en mémoire
  - `jmp 0x6011000` pour lancer le shellcode
* le shellcode est généré par metasploit et fait un `execve("/bin/sh", 0, 0)`

Pour tester:
```
python solving_script.py > payload
cat payload - | nc localhost 5555
```
Ceci devrait vous donner un shell. Vous n'avez plus qu'à `cat flag`.
