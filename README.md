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

フロントエンドは自由に実装できるため、教育機関などクローズドな環境で使用するのもよいでしょう。

## 検証環境

 - Alma Linux 9
 - Python 3.9.10
 - MySQL 8.0.31 (MySQL Community Server - GPL)
 - Screen version 4.06.02 (GNU) 23-Oct-17

## Install

実行に必要な前準備をします。環境によっては不要かもしれません。

```
dnf install python python3-pip python-devel
pip3 install -r requirements.txt
pip3 install mysql-connector-python

sudo dnf install https://dl.fedoraproject.org/pub/epel/epel-release-latest-9.noarch.rpm -y
sudo dnf install screen -y
```

MySQL の利用のため、設定を記述します。`app/config.example` を `app/config` にリネームし、適切に書き換えてください。

以上が終わったら、セットアップスクリプトを実行します。下記を実行すると、`127.0.0.1:8000` で WebAPI が動作します。  
必要があれば、リバースプロキシ等でホスト名やポートを設定してください。本 README.md では、これ以降 `example.com:80` で動作しているものとします。

また、セットアップスクリプトには systemd に登録する記述が含まれているため、以降は systemd より管理することができます。

```
./setup.sh
```

## Usage

### Registration

以下の curl コマンドのような HTTP リクエストで id と username を指定することで、自動的に uuid が生成され、データベースにユーザが登録されます。

```
curl -X POST "example.com/register" -H 'Content-Type: application/json' -d '{"id":"foo","username":"Testuser", "password": "password"}'
```

### Post

以下の curl コマンドのような HTTP リクエストで付箋を投稿することができます。

```
curl -X POST "example.com/post" -H 'Content-Type: application/json' -d '{"isbn": "9784274223570", "page": 1, "x": 0.5, "y": 0.5, "type": 0, "account_uuid": "00000your-uuid00000", "content": "This is first post in this service"}'
```

それぞれの値については以下の通りです。

|  Parameter  |  Description  |
| ---- | ---- |
|  isbn  | ISBN です。ハイフン等を使用せず、数字のみの 13 桁で入力してください。  |
|  page  | 該当箇所のペース番号です。  |
|  x  |  該当箇所の x 座標です。0 <= x <= 1 であり、ページの左上を原点として、右側の何 % の部分であるかを入力してください。<br>ex. 10cm の横幅のページのとき、x = 0.3 であれば左から 3cm の部分。  |
|  y  |  該当箇所の y 座標です。0 <= y <= 1 であり、ページの左上を原点として、下側の何 % の部分であるかを入力してください。<br>ex. 10cm の縦幅のページのとき、y = 0.3 であれば上から 3cm の部分。  |
|  type  |  投稿の種別です。詳しくは下部の表を参照してください。  |
|  account_uuid  | 投稿者のアカウントの UUID です。  |
|  content  |  投稿の内容。極力、Markdown 記法をサポートするようにしてください。  |

type の値の詳細については以下の通りです。

|  Value  |  Description  |
| ---- | ---- |
|  0  |  一般ユーザの投稿。わかりにくく、つまずいた部分。  |
|  1  |  一般ユーザの投稿。ユーザによる補足説明。  |
|  2  |  一般ユーザの投稿。演習などの追加解説や別解。  |
|  3  |  公式ユーザの投稿。公式による補足説明。  |
|  4  |  公式ユーザの投稿。演習などの追加解説や別解。  |

### Get books

以下の curl コマンドのような HTTP リクエストで付箋の登録されている本の ISBN を取得することができます。

```
curl example.com/getbooks
```

上記のコマンドを実行すると、以下の値が得られます。

```
{"state":true,"data":[{"isbn":"9784274223570","posts":2}]}
```


### Get posts

以下の curl コマンドのような HTTP リクエストで投稿された付箋を取得することができます。

```
# curl example.com/getposts/{isbn}
curl example.com/getposts/9784274223570
```

上記のコマンドを実行すると、以下の値が得られます。

```
{"state": true, "data":[{"postid":"15497259-8ea2-43b2-bbc2-90c0ba52868d","page":1,"x":0.5,"y":0.5,"type":0,"postdate":20221117181806,"updatedate":null,"account_uuid":"0a891785-9484-44e6-b1ea-970792223739","content":"This is first post in this service"},{"postid":"2402e745-179e-4d0a-bb66-d63789d0a5b8","page":1,"x":0.5,"y":0.5,"type":0,"postdate":20221118061359,"updatedate":null,"account_uuid":"0a891785-9484-44e6-b1ea-970792223739","content":"This is the second post in this service"}]}
```

Python では、`data` をキーとして、それぞれのデータの辞書のリストが返ってくる形であることに注意してください。

### Show users

以下の curl コマンドのような HTTP リクエストで入力した ID に一致するユーザの情報を取得することができます。

```
curl example.com/users/foo
```

それぞれの値については以下の通りです。

|  Parameter  |  Description  |
| ---- | ---- |
|  state  |  値の取得状況。正常に終了していれば、true が返る。  |
|  message  |  state が false であれば返され、その旨を伝えるメッセージが含まれる。  |
|  id  |  ユーザの ID。  |
|  username  |  ユーザ名。ID とは異なる。  |
|  usermode  |  ユーザの持つ権限。  |
|  posts  |  投稿数。  |
|  goods  |  ユーザの獲得したいいね数。(未実装)  |
|  registerdate  |  ユーザの登録日時。  |
|  verify  |  ユーザの認証状況。認証済みアカウントであれば 1、そうでなければ 0。  |

#### Usermode

データベース内ではユーザ情報として権限の情報を保持しています。  
以下の表より、持つ権限に合ったそれぞれの数字の総和が保持されます。

|  Permission  |  Value  |
| ---- | ---- |
|  Read  |  1  |
|  Post  |  2  |
|  Admin  |  4  |

例えば、3 を持つ場合はデータの取得と投稿ができます。

また、0 を持つ場合は一切の権限を持ちません。

現状、以下の通りになっています。

 - 登録時に config で設定したデフォルト値が適用される
   - デフォルト: 3
 - データベースを直接変更することでのみ変更可能

### Favorite

以下の curl コマンドのような HTTP リクエストでアカウントの UUID と付箋の Post ID を指定することで、付箋がお気に入り登録されます。

```
curl -X POST "example.com/register" -H 'Content-Type: application/json' -d '{"type":0, "account_uuid":"0a891785-9484-44e6-b1ea-970792223739", "postid":"5c266c27-c598-4a26-8147-c57567a303e9"}'
```

### Favorite list

以下の curl コマンドのような HTTP リクエストでユーザがお気に入り登録した付箋を取得することができます。

```
# curl example.com/favlist/{id}
curl example.com/favlist/foo
```

上記のコマンドを実行すると、以下の値が得られます。

```
{"state":true,"data":[{"type":0,"id":"foo","postid":"5c266c27-c598-4a26-8147-c57567a303e9","date":20221223054401}]}
```

#### Type

データベース内ではお気に入りの種別を保持しています。

|  Type  |  Value  |
| ---- | ---- |
|  Normal  |  0  |

### Thread

スレッドを作成できます。それぞれのスレッドにチャットを投稿することで、様々な議論ができます。

以下の curl コマンドのような HTTP リクエストでスレッドを作成できます。

```
curl -X POST "example.com/createthread" -H 'Content-Type: application/json' -d '{"title":"first thread","type":0,"account_uuid":"0a891785-9484-44e6-b1ea-970792223739"}'
```

### Post chat

以下の curl コマンドのような HTTP リクエストでスレッドに投稿できます。

```
curl -X POST "example.com/postchat" -H 'Content-Type: application/json' -d '{"thread":1,"account_uuid":"0a891785-9484-44e6-b1ea-970792223739", "content":"can you see me?"}'
```

### Get threads

以下の curl コマンドのような HTTP リクエストで存在しているスレッドを取得できます。

```
curl example.com/getthreads
```

上記のコマンドを実行すると、以下のような値が得られます。

```
{"state":true,"data":[{"number":1,"title":"first thread","date":20230112133006,"type":0,"account_uuid":"0a891785-9484-44e6-b1ea-970792223739"},{"number":2,"title":"second thread","date":20230112133107,"type":0,"account_uuid":"0e4fa882-ff41-4b85-87ea-4c1b879aacc5"}]}
```

### Get chats

以下の curl コマンドのような HTTP リクエストで存在しているスレッドを取得できます。

```
curl example.com/getchats/1
```

上記のコマンドを実行すると、以下のような値が得られます。

```
{"state":true,"data":[{"postid":"1e0a9b99-f26a-4eff-a377-50076d03416e","thread":1,"postdate":20230112133846,"account_uuid":"0a891785-9484-44e6-b1ea-970792223739","content":"can you see me?"},{"postid":"8f71bdaf-c94f-4ab2-b870-eb25edb57658","thread":1,"postdate":20230112133944,"account_uuid":"0e4fa882-ff41-4b85-87ea-4c1b879aacc5","content":"yes"}]}
```

## DONE

 - ユーザの登録
   - 登録日や認証ユーザ、投稿数などのデータを保持するように変更
 - 付箋の登録
   - ISBN, ページ数, 位置, 付箋の種別, 投稿日時, 更新日時, 投稿者 UUID, 内容を保持
 - セットアップスクリプトの作成
   - 実行すると systemd から管理できるように
 - コミュニティ機能の実装
   - スレッド

## TODO

 - 付箋の登録
   - 削除
   - 編集
 - ユーザの権限管理
   - 現状でユーザ情報に 'usermode' を付与済み

### Extra

 - パスワード保存方法の見直し
   - DB 登録時はハッシュ化しているけど、ソルトとか全く触ってないので微妙かもしれない
   - あと、HTTPS なら登録時に生のパスワードを送信しても良いのか？という気持ちもある
 - systemd での管理の最適化
   - `systemctl stop projectapi.service` してから `systemctl status projectapi.service` を見ると、正しく終了されていない気がする
 - 攻撃対策
   - 現状何もしていません。結構まずいかも。
     - CSRF 関連の把握, SQL インジェクション対策

## 参考
https://qiita.com/yota_dev/items/ab8dea7f71c8a130d5bf


