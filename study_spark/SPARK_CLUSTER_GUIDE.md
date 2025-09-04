# 🚀 Spark Cluster Management Guide

## 📋 Зміст
- [Налаштування SPARK_HOME](#налаштування-spark_home)
- [Запуск кластера](#запуск-кластера)
- [Перевірка статусу](#перевірка-статусу)
- [Запуск додатків](#запуск-додатків)
- [Зупинка кластеру](#зупинка-кластеру)
- [Після перезапуску Cursor](#після-перезапуску-cursor)
- [UI посилання](#ui-посилання)
- [Важливі команди](#важливі-команди)

---

## ⚙️ Налаштування SPARK_HOME

### Додати до ~/.zshrc (вже зроблено)
```bash
export SPARK_HOME=/Users/admin/Desktop/git_rep/spark_local
export PATH=$SPARK_HOME/bin:$PATH
```

### Перезавантажити профіль
```bash
source ~/.zshrc
```

---

## 🎯 Запуск кластера

### 1. Запустити Master
```bash
$SPARK_HOME/sbin/start-master.sh
```
**UI доступний на**: http://localhost:8080

### 2. Запустити Worker з налаштуваннями ресурсів
```bash
# Базовий запуск
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077

# З налаштуванням кількості ядер
$SPARK_HOME/sbin/start-worker.sh --cores 4 spark://localhost:7077

# З налаштуванням пам'яті
$SPARK_HOME/sbin/start-worker.sh --memory 2g spark://localhost:7077

# З налаштуванням ядер та пам'яті
$SPARK_HOME/sbin/start-worker.sh --cores 4 --memory 2g spark://localhost:7077
```
**UI доступний на**: http://localhost:8081

### 3. Налаштування ресурсів через конфігурацію

#### Створити/редагувати конфігурацію Worker'а
```bash
# Відкрити конфігурацію
nano $SPARK_HOME/conf/spark-defaults.conf

# Додати налаштування
spark.worker.cores=4
spark.worker.memory=2g
spark.worker.memoryOverhead=512m
```

#### Налаштування через змінні середовища
```bash
# Встановити змінні перед запуском
export SPARK_WORKER_CORES=4
export SPARK_WORKER_MEMORY=2g
export SPARK_WORKER_MEMORY_OVERHEAD=512m

# Запустити Worker
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077
```

### 4. Налаштування Master'а

#### Запуск Master з параметрами
```bash
# З налаштуванням порту
$SPARK_HOME/sbin/start-master.sh --port 7077

# З налаштуванням хоста
$SPARK_HOME/sbin/start-master.sh --host 0.0.0.0

# З налаштуванням UI порту
$SPARK_HOME/sbin/start-master.sh --webui-port 8080
```

#### Налаштування Master через конфігурацію
```bash
# Відкрити конфігурацію
nano $SPARK_HOME/conf/spark-defaults.conf

# Додати налаштування Master'а
spark.master.port=7077
spark.master.webui.port=8080
spark.master.rest.port=6066
```

### 5. Додаткові параметри Worker'а

#### Розширені налаштування
```bash
# Запуск з додатковими параметрами
$SPARK_HOME/sbin/start-worker.sh \
  --cores 4 \
  --memory 2g \
  --memory-overhead 512m \
  --webui-port 8081 \
  --properties-file $SPARK_HOME/conf/spark-defaults.conf \
  spark://localhost:7077
```

#### Налаштування через файл конфігурації
```bash
# Створити/редагувати spark-env.sh
nano $SPARK_HOME/conf/spark-env.sh

# Додати налаштування
export SPARK_WORKER_CORES=4
export SPARK_WORKER_MEMORY=2g
export SPARK_WORKER_MEMORY_OVERHEAD=512m
export SPARK_WORKER_WEBUI_PORT=8081
```

---

## 🔍 Перевірка статусу

### Перевірити процеси
```bash
ps aux | grep spark
```

### Перевірити змінну
```bash
echo $SPARK_HOME
```

### Перевірити доступні команди
```bash
which spark-submit
```

---

## 📊 Запуск додатків

### Запустити Python скрипт на кластері
```bash
spark-submit --master spark://localhost:7077 study_spark/batch03.py
```

### Запустити з додатковими параметрами
```bash
spark-submit --master spark://localhost:7077 --executor-memory 2g study_spark/batch03.py
```

---

## 🛑 Зупинка кластеру

### Зупинити все одразу
```bash
$SPARK_HOME/sbin/stop-all.sh
```

### Зупинити окремо
```bash
# Зупинити Worker
$SPARK_HOME/sbin/stop-worker.sh

# Зупинити Master
$SPARK_HOME/sbin/stop-master.sh
```

---

## 🔄 Після перезапуску Cursor

### 1. Перевірити чи працюють процеси
```bash
ps aux | grep spark
```

### 2. Якщо потрібно, перезавантажити змінні
```bash
source ~/.zshrc
```

### 3. Перевірити SPARK_HOME
```bash
echo $SPARK_HOME
```

---

## 🌐 UI посилання

- **Master UI**: http://localhost:8080
- **Worker UI**: http://localhost:8081
- **Application UI**: http://localhost:4040 (під час виконання)

---

## ⚠️ Важливі команди

### Перейти в папку Spark
```bash
cd $SPARK_HOME
```

### Переглянути логи
```bash
ls -la logs/
```

### Переглянути конфігурацію
```bash
ls -la conf/
```

### Переглянути доступні скрипти
```bash
ls -la sbin/
```

### Перевірити налаштування ресурсів
```bash
# Перевірити конфігурацію
cat $SPARK_HOME/conf/spark-defaults.conf

# Перевірити змінні середовища
env | grep SPARK

# Перевірити процеси та їх ресурси
ps aux | grep spark
```

---

## 📝 Приклади використання

### Повний цикл роботи
```bash
# 1. Запустити кластер
$SPARK_HOME/sbin/start-master.sh
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077

# 2. Запустити додаток
spark-submit --master spark://localhost:7077 study_spark/batch03.py

# 3. Зупинити кластер
$SPARK_HOME/sbin/stop-all.sh
```

### Запуск з налаштуваннями ресурсів
```bash
# 1. Запустити Master
$SPARK_HOME/sbin/start-master.sh --webui-port 8080

# 2. Запустити Worker з ресурсами
$SPARK_HOME/sbin/start-worker.sh \
  --cores 4 \
  --memory 2g \
  --webui-port 8081 \
  spark://localhost:7077

# 3. Запустити додаток з обмеженнями
spark-submit \
  --master spark://localhost:7077 \
  --executor-cores 2 \
  --executor-memory 1g \
  study_spark/batch03.py
```

### Перевірка роботи
```bash
# Перевірити статус
ps aux | grep spark

# Відкрити UI в браузері
open http://localhost:8080
open http://localhost:8081
```

---

## 🎉 Висновок

Цей гайд містить всі основні команди для управління твоїм Spark кластером. Після налаштування SPARK_HOME, ти можеш легко запускати, зупиняти та керувати кластером за допомогою простих команд.

**Головне**: Master і Worker залишаються працювати навіть після закриття Cursor, але SPARK_HOME потрібно перезавантажувати. 