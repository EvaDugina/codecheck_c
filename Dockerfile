# Используем официальный образ Python
FROM python:3.11-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    g++ clang-format valgrind cppcheck
    # locales \
    # && rm -rf /var/lib/apt/lists/*

# Настройка локали
# RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
# ENV LANG en_US.UTF-8
# RUN mkdir -p ~/.config/pip/ && echo "[global]" >> ~/.config/pip/pip.conf \
#     && echo "break-system-packages = true" >> ~/.config/pip/pip.conf
# RUN pip install copydetect
COPY ./ /tmp/

RUN cd /tmp/ && chmod 777 -R ./ && pip install . && cd /

VOLUME /tmp

WORKDIR /tmp