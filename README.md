# スーパー参考書メーカー

## Summary

法政大学情報科学部首藤プロジェクト 2022 秋  
2-10 スーパー参考書メーカーのリポジトリです。

主となる機能は、ISBN とページ数、位置、内容で管理されたデジタル付箋をデータベースで管理、各ユーザが自由に登録、参照することです。  
これらのデータを多く収集することで、参考書における難解な部分を明確にします。その結果、以下のような効果が見込めます。

 - 学習者の躓いたポイントが、他の学習者も同様であるのかを明確にできる
 - 教師は、多くの学生が躓くポイントを重点的に指導し、そうでない部分に時間を割かないようにできる
 - 出版社側は、多くの学習者が躓くポイントを把握し、修正できる
 - 演習の正答率やよくある誤答の蓄積

また、コミュニティを形成することで、以下の結果も得られるでしょう。

 - ユーザ/公式による補足説明
 - 参考書にはない、演習の別解の掲載
 - ユーザの学習レベルを設定し統計的に処理することで、各ユーザのレベルに合った参考書をレコメンド

このリポジトリのものは主にバックエンドで稼働する部分です。

HTTP でリクエストを受信し、それに合わせて動作します。

## 検証環境

 - Alma Linux 9
 - Python 3.9.10
 - MySQL 8.0.31 (MySQL Community Server - GPL)

## Install

実行に必要な前準備をします。環境によっては不要かもしれません。

```
dnf install python python3-pip python-devel
pip3 install -r requirements.txt
pip3 install mysql-connector-python
```

MySQL の利用のため、設定を記述します。`app/config.example` を `app/config` にリネームし、適切に書き換えてください。

以上が終わったら、実行します。

```
cd app
uvicorn main:app --reload
```

## Usage

### Registration

以下の curl コマンドのような HTTP リクエストで id と username を指定することで、自動的に uuid が生成され、データベースにユーザが登録されます。

```
curl -X POST "example.com/register" -H 'Content-Type: application/json' -d '{"id":"foo","username":"Testuser"}'
```

## DONE

 - ユーザの登録

## TODO

 - 付箋の登録
   - ISBN, ページ数, 位置, 内容, 付箋の種別
     - 付箋の種別: 疑問, 補足, 別解等?
   - 削除
   - 編集
 - MySQL 等の設定を外部の config から読み込み
 - シェルスクリプト or systemd による service 化で実行
 - ユーザの権限管理
   - 現状でユーザ情報に 'usermode' を付与済み

### Extra

 - コミュニティ機能の実装
   - スレッド等

## 参考
https://qiita.com/yota_dev/items/ab8dea7f71c8a130d5bf


