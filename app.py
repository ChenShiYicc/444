import time
import random
import re
import requests
from bs4 import BeautifulSoup
import jieba
from collections import Counter
import streamlit as st
from pyecharts import options as opts
from pyecharts.charts import WordCloud, Bar, Line, Pie, Scatter
from pyecharts.commons.utils import JsCode
from streamlit.components.v1 import html

# 步骤 1：抓取网页内容
def fetch_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            response.encoding = response.apparent_encoding
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup.get_text(separator=' ', strip=True)
    except requests.exceptions.RequestException as e:
        st.error(f"请求异常: {e}")
    except Exception as e:
        st.error(f"发生错误: {e}")

# 步骤 2：文本预处理
def preprocess_text(text):
    text = re.sub(r'<[^>]+>', '', text)  # 去除HTML标签
    text = re.sub(r'[^\w\s]', '', text)  # 去除标点符号
    return text

# 步骤 3：分词和统计词频
def word_segmentation_and_count(text):
    words = jieba.cut(text)
    word_count = Counter(words)
    return word_count

# 步骤 4：生成图表
def generate_chart(word_count, chart_type):
    if chart_type == "词云图":
        wc = WordCloud()
        wc.add("词云", list(word_count.items()), word_size_range=[10, 30])
        wc.set_global_opts(title_opts=opts.TitleOpts(title="词云图"))
        return wc
    elif chart_type == "词频柱状图":
        bar = Bar()
        top_words = word_count.most_common(20)
        words, counts = zip(*top_words)
        bar.add_xaxis(list(words))
        bar.add_yaxis("词频", list(counts))
        bar.set_global_opts(title_opts=opts.TitleOpts(title="词频柱状图"))
        return bar
    elif chart_type == "词频条形图":
        bar = Bar(init_opts=opts.InitOpts(width="1000px", height="600px"))
        bar.add_xaxis(list(word_count.keys()))
        bar.add_yaxis("词频", list(word_count.values()),
                      label_opts=opts.LabelOpts(position="right"),
                      category_gap="50%")
        bar.reversal_axis()
        bar.set_global_opts(
            title_opts=opts.TitleOpts(title="词频条形图"),
            xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=-15)),
            yaxis_opts=opts.AxisOpts(name="词频"),
        )
        return bar
    elif chart_type == "词频折线图":
        line = Line()
        top_words = word_count.most_common(20)
        words, counts = zip(*top_words)
        line.add_xaxis(list(words))
        line.add_yaxis("词频", list(counts))
        line.set_global_opts(title_opts=opts.TitleOpts(title="词频折线图"))
        return line
    elif chart_type == "词频饼图":
        pie = Pie()
        top_words = word_count.most_common(10)
        words, counts = zip(*top_words)
        pie.add("", [list(z) for z in zip(words, counts)])
        pie.set_global_opts(title_opts=opts.TitleOpts(title="词频饼图"))
        return pie
    elif chart_type == "词频散点图":
        scatter = Scatter()
        words = list(word_count.keys())
        counts = list(word_count.values())
        scatter.add_xaxis(words)
        scatter.add_yaxis("词频", counts)
        scatter.set_global_opts(title_opts=opts.TitleOpts(title="词频散点图"))
        return scatter

# 步骤 5：渲染图表
def render_chart(chart):
    html_code = chart.render_embed()
    html(html_code, height=600)

# Streamlit UI
def main():
    st.title('文章词频分析与词云展示')
    url = st.text_input("请输入文章URL:")
    if url:
        text = fetch_content(url)
        if not text:
            st.warning("未抓取到网页内容，请检查URL或网站内容。")
            return
        st.subheader("抓取的网页内容")
        st.write(text[:500] + '...')
        clean_text = preprocess_text(text)
        st.subheader("预处理后的文本")
        st.write(clean_text[:500] + '...')
        word_count = word_segmentation_and_count(clean_text)
        st.subheader('词频排名前20的词')
        top_20_words = word_count.most_common(20)
        for word, freq in top_20_words:
            st.write(f"{word}: {freq}")
        chart_type = st.selectbox(
            "选择图形类型",
            ["词云图", "词频柱状图", "词频条形图", "词频折线图", "词频饼图", "词频散点图"]
        )
        if chart_type:
            chart = generate_chart(word_count, chart_type)
            render_chart(chart)

if __name__ == '__main__':
    main()