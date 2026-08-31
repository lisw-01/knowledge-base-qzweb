
##  删除文件  

rm file	删除文件，有提示
rm -f file	强制删文件，无提示
rm -r dir	删除目录，会提示
rm -rf dir	强制递归删除目录，无提示
rm -i file	删除前逐个确认


##  删除文件夹


rm -rf dir	强制删除文件夹（有内容也删）
rm -ri dir	删除前交互确认
rmdir dir	仅删除空文件夹

##  清空当前目录下的所有文件

rm -rf ./*



##  解压 .zip文件
unzip test.zip
