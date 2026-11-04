# FlakeSeed

Pytest sırasını karıştırır, aynı hatayı üreten diziyi arar, kısaltır ve tekrar oynatır.

## Kullanım

Python 3.11 veya üzeri.

```sh
python -m pip install -r requirements.txt
python flakeseed.py --seed 1 --attempts 10 -o order.json
```

Test reposunun kökünden çalıştır. Kayıt için 1, hata üretilemezse 0 döndürür. Tekrar oynatmak için --replay order.json kullan. Seri pytest çalışması içindir.

## Doğrulama

```sh
python verify.py
```

MIT lisansı.
