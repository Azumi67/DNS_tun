![R (2)](https://github.com/Azumi67/PrivateIP-Tunnel/assets/119934376/a064577c-9302-4f43-b3bf-3d4f84245a6f)
نام پروژه : تانل dns 
--
![check](https://github.com/Azumi67/PrivateIP-Tunnel/assets/119934376/13de8d36-dcfe-498b-9d99-440049c0cf14)
**امکانات**
- تانل dns 
- امکان مشخص کردن ایپی پرایوت ورژن 4 به صورت custom 
- امکان ویرایش تانل
- امکان مشاهده لاگ سرویس
- دارای ریست تایمر
- دارای input های متفاوت برای بهترین نتیجه
- امکان حذف تانل
- دارای ریست تایمر
-----------------------
 ![6348248](https://github.com/Azumi67/PrivateIP-Tunnel/assets/119934376/398f8b07-65be-472e-9821-631f7b70f783)
**آموزش استفاده از اسکریپت**

- قبل از اینکه اسکریپت را اجرا کنم باید یک دامین تهیه کنم. به طور مثال دامین من azumi.com است . حالا داخل dns provider باید یک NS با عنوان tunnel و مقدار iodine.azumi.beauty. ( حتما در اخر مقدار یک dot قرار دهید) و یک رکورد A با عنوان iodine و ایپی پابلیک سرور خارج قرار میدهم. در اسکریپت از ساب دامین tunnel.iodine.azumi.com استفاده میکنم. اگر فرایند را درست انجام دهید، تانل برای شما باید فعال شود و بین دو پرایوت ایپی پینگ برقرار شود.
 <div align="right">
  <details>
    <summary><strong><img src="https://github.com/Azumi67/Rathole_reverseTunnel/assets/119934376/fcbbdc62-2de5-48aa-bbdd-e323e96a62b5" alt="Image"> </strong>نحوه استفاده از اسکریپت</summary>

------------------
<p align="right">
  <img src="https://github.com/user-attachments/assets/18956680-bcf1-4f02-add4-0acd30fe0abd" alt="Image" />
</p>

- نخست پسورد را وارد میکنم
- ایپی پرایوت ورژن 4 را وارد میکنم
- ساب دامین که پشت ان ایپی سرور خارج را قرار داده ام، وارد میکنم
- ساب دامین را tunnel.iodine.azumi.com (همانی که ساختم)، قرار میدهم.
- مقدار mtu را به صورت دیفالت 1130 وارد میکنم. شما میتوانید تغییر دهید
- نام دیوایس را dns2 قرار میدهم
<p align="right">
  <img src="https://github.com/user-attachments/assets/bc5be169-837b-4990-b1a9-aabad81c1b31" alt="Image" />

- نام پسورد را ازومی قرار میدهم
- پابلیک ایپی سرور خارج را وارد میکنم
- نام ساب دامینی را که در سرور وارد کردم اینجا هم وارد میکنم
- مقدار فرگمنت را 100 قرار میدهم شما میتوانید 200 قرار بدهید
- مقدار dns query را txt یا null قرار میدهم
- مقدار keepalive را 30 ثانیه قرار میدهم
- نام دیوایس را مشخص میکنم
</details>
</div>

----------------
**- نصب پیش نیاز ها**
```
apt install python3 -y && sudo apt install python3-pip &&  pip install colorama && pip install netifaces && apt install curl -y
pip3 install colorama
sudo apt-get install python-pip -y  &&  apt-get install python3 -y && alias python=python3 && python -m pip install colorama && python -m pip install netifaces
sudo apt update -y && sudo apt install -y python3 python3-pip curl && pip3 install --upgrade pip && pip3 install netifaces colorama requests

```
- اجرای اسکریپت
```
apt install curl -y && bash -c "$(curl -fsSL )"
```
