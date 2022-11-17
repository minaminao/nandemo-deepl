# Sample
参考：[Markdown Cheatsheet · adam-p/markdown-here Wiki](https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet)

## Headers
# H1
## H2
### H3
#### H4
##### H5
###### H6
あるいは、H1やH2には、アンダーライン的なスタイルで。

Alt-H1
======
Alt-H2
------
## Emphasis
*asterisks*または*underscores*で強調表示、別名イタリック体。

**asterisks**または**underscores**で強い強調、別名ボールド。

**asterisks and *underscores***との複合強調。

取り消し線はチルダを2つ使用します。~~Scratch this.~~

## Lists
1. First ordered list item

2. Another item

  * Unordered sub-list.

1. Actual numbers don't matter, just that it's a number

  1. Ordered sub-list

2. And another item.

リストアイテムの中で適切にインデントされた段落を作成することができます。上の空白行と、先頭のスペースに注目してください (最低でも1つ、しかしここでは生のMarkdownを揃えるために3つのスペースを使用します)。

段落を作らずに改行するには、最後に空白を2つ入れる必要があります⋅⋅⋅⋅。
この行は独立していますが、同じ段落の中にあることに注意してください。
(これは、GFMの典型的な改行動作とは異なり、末尾のスペースは必要ありません)。

* Unordered list can use asterisks

- Or minuses

+ Or pluses

## Links
[I'm an inline-style link](https://www.google.com)

[I'm an inline-style link with title](https://www.google.com)

[I'm a reference-style link](https://www.mozilla.org)

[I'm a relative reference to a repository file](../blob/master/LICENSE)

[You can use numbers for reference-style link definitions](http://slashdot.org)

または、空のまま[link text itself](http://www.reddit.com)を使用する。

URLや角括弧の中のURLは自動的にリンクになります。
http://www.example.com、または<http://www.example.com>、時には
example.com（ただし、Githubなどでは不可）。

参照リンクが後からついてくることを示すためのテキストをいくつか。

## Images
これが私たちのロゴです（カーソルを合わせるとタイトル文字が表示されます）。

インラインスタイル
![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 1")

参考スタイル
![alt text](https://github.com/adam-p/markdown-here/raw/master/src/common/images/icon48.png "Logo Title Text 2")

## Code and Syntax Highlighting
インライン`code`は`back-ticks around`がそれ。

```javascript
var s = "JavaScript syntax highlighting";
alert(s);
```
```python
s = "Python syntax highlighting"
print s
```
```
No language indicated, so no syntax highlighting. 
But let's throw in a <b>tag</b>.
```
## Tables
コロンで列を揃えることができる。

各ヘッダーセルを区切るダッシュは最低3本必要です。
外側のパイプ (|) はオプションです。
生のMarkdownをきれいに並べる必要はありません。あなたはインラインMarkdownを使用することもできます。

## Blockquotes
> ブロッククオートは、電子メールにおいて返信用のテキストを模倣するために非常に便利です。
この行は、同じ引用文の一部です。

引用ブレーク。

> これはとても長い行で、ラップしてもちゃんと引用されます。やれやれ......これが実際に折り返すのに十分な長さであることを皆に確認するために、書き続けましょう。あ、*put* **Markdown**をブロッククオートにすることもできますよ。

## Inline HTML
<dl>

<dt>Definition list</dt>

<dd>Is something people use sometimes.</dd>

<dt>Markdown in HTML</dt>

<dd>Does *not* work **very** well. Use HTML <em>tags</em>.</dd>

</dl>

## Horizontal Rule
3つ以上...

---
ハイフン

---
アスタリスク

---
アンダースコア

## Line Breaks
ここで、まずは1行だけご紹介します。

この行は上の行と改行2つで区切られているので、*separate paragraph*になります。

この行も独立した段落になっていますが
この行は改行1つで区切られているだけなので、*same paragraph*では独立した行になっています。

## YouTube Videos
<a href="http://www.youtube.com/watch?feature=player_embedded&v=YOUTUBE_VIDEO_ID_HERE
" target="_blank"><img src="http://img.youtube.com/vi/YOUTUBE_VIDEO_ID_HERE/0.jpg"
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>
