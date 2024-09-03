Git pull just smokepeer
```
git clone --no-checkout https://github.com/Strykar/Livepeer.git
cd Livepeer
git sparse-checkout init --cone
git sparse-checkout set smokeping/smokepeer
git pull origin main
```

To push:
```
cd smokeping/smokepeer
git add .
git commit -m "Smoke peer all day"
git push origin main
```
