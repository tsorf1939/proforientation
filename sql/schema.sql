-- =============================================================
-- Схема БД: Платформа профориентации для школьников
-- =============================================================

-- 1. Таблица школ
CREATE TABLE IF NOT EXISTS schools (
    school_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    address VARCHAR(200),
    phone VARCHAR(20)
);

-- 2. Таблица учащихся
CREATE TABLE IF NOT EXISTS students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    school_id INT REFERENCES schools(school_id),
    grade INT CHECK (grade BETWEEN 1 AND 11),
    email VARCHAR(100) UNIQUE,
    registration_date DATE DEFAULT CURRENT_DATE
);

-- 3. Таблица профессий
CREATE TABLE IF NOT EXISTS professions (
    profession_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    avg_salary DECIMAL(10,2),
    demand_level INT CHECK (demand_level BETWEEN 1 AND 5),
    universities JSONB DEFAULT '[]'
);

-- 4. Таблица тестов
CREATE TABLE IF NOT EXISTS tests (
    test_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    questions_count INT DEFAULT 0,
    duration_minutes INT,
    test_type VARCHAR(20) DEFAULT 'career' CHECK (test_type IN ('career', 'klimov', 'temperament', 'scored', 'reflection')),
    task_number INT
);

-- 5. Таблица вопросов теста
CREATE TABLE IF NOT EXISTS test_questions (
    question_id SERIAL PRIMARY KEY,
    test_id INT REFERENCES tests(test_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) DEFAULT 'single_choice',
    question_order INT DEFAULT 0
);

-- 6. Варианты ответов с весами по категориям Казаковой
CREATE TABLE IF NOT EXISTS answer_options (
    option_id SERIAL PRIMARY KEY,
    question_id INT REFERENCES test_questions(question_id) ON DELETE CASCADE,
    option_text VARCHAR(300) NOT NULL,
    weight_people INT DEFAULT 0,
    weight_intellectual INT DEFAULT 0,
    weight_practical INT DEFAULT 0,
    weight_aesthetic INT DEFAULT 0,
    weight_physical INT DEFAULT 0,
    weight_administrative INT DEFAULT 0
);

-- 7. Таблица ответов учащихся
CREATE TABLE IF NOT EXISTS student_answers (
    answer_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    question_id INT REFERENCES test_questions(question_id),
    answer_text TEXT,
    option_id INT REFERENCES answer_options(option_id)
);

-- 8. Таблица результатов тестирования
CREATE TABLE IF NOT EXISTS test_results (
    result_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    test_id INT REFERENCES tests(test_id),
    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'в_процессе' CHECK (status IN ('в_процессе', 'завершено')),
    UNIQUE (student_id, test_id)
);

-- 9. Таблица рекомендаций профессий
CREATE TABLE IF NOT EXISTS profession_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    result_id INT REFERENCES test_results(result_id) ON DELETE CASCADE,
    profession_id INT REFERENCES professions(profession_id),
    match_percentage DECIMAL(5,2) CHECK (match_percentage BETWEEN 0 AND 100),
    recommendation_level INT CHECK (recommendation_level BETWEEN 1 AND 3)
);

-- 10. Глобальные рекомендации профессий (на основе нескольких тестов)
CREATE TABLE IF NOT EXISTS student_recommendations (
    recommendation_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    profession_id INT REFERENCES professions(profession_id) ON DELETE CASCADE,
    match_percentage DECIMAL(5,2) CHECK (match_percentage BETWEEN 0 AND 100),
    recommendation_level INT CHECK (recommendation_level BETWEEN 1 AND 3),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, profession_id)
);

-- 11. Веса профессий по категориям Казаковой
CREATE TABLE IF NOT EXISTS profession_type_weights (
    id SERIAL PRIMARY KEY,
    profession_id INT UNIQUE REFERENCES professions(profession_id) ON DELETE CASCADE,
    weight_people INT DEFAULT 0,
    weight_intellectual INT DEFAULT 0,
    weight_practical INT DEFAULT 0,
    weight_aesthetic INT DEFAULT 0,
    weight_physical INT DEFAULT 0,
    weight_administrative INT DEFAULT 0
);

-- 11. Django auth users (создаётся Django, здесь для справки)
-- auth_user создаётся автоматически через manage.py migrate

-- 12. Связь студента с Django-пользователем
CREATE TABLE IF NOT EXISTS student_users (
    id SERIAL PRIMARY KEY,
    student_id INT UNIQUE REFERENCES students(student_id) ON DELETE CASCADE,
    django_user_id INT UNIQUE NOT NULL
);

-- 13. Учителя
CREATE TABLE IF NOT EXISTS teachers (
    teacher_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    school_id INT REFERENCES schools(school_id),
    email VARCHAR(100) UNIQUE NOT NULL,
    django_user_id INT UNIQUE NOT NULL
);

-- 14. Привязка учителя к классам
CREATE TABLE IF NOT EXISTS teacher_classes (
    id SERIAL PRIMARY KEY,
    teacher_id INT REFERENCES teachers(teacher_id) ON DELETE CASCADE,
    grade INT CHECK (grade BETWEEN 1 AND 11),
    school_id INT REFERENCES schools(school_id),
    UNIQUE (teacher_id, grade, school_id)
);

-- 15. Отчёты по классам
CREATE TABLE IF NOT EXISTS class_reports (
    report_id SERIAL PRIMARY KEY,
    teacher_id INT REFERENCES teachers(teacher_id),
    grade INT,
    school_id INT REFERENCES schools(school_id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data JSONB DEFAULT '{}'
);

-- =============================================================
-- ТРИГГЕРЫ
-- =============================================================

-- 1. Проверка возраста учащегося (>6 лет)
CREATE OR REPLACE FUNCTION check_student_age()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.birth_date IS NOT NULL AND EXTRACT(YEAR FROM AGE(NEW.birth_date)) < 6 THEN
        RAISE EXCEPTION 'Учащийся должен быть старше 6 лет';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_check_age ON students;
CREATE TRIGGER trigger_check_age
BEFORE INSERT OR UPDATE ON students
FOR EACH ROW EXECUTE FUNCTION check_student_age();

-- 2. Автообновление questions_count при добавлении/удалении вопроса
CREATE OR REPLACE FUNCTION update_questions_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE tests SET questions_count = questions_count + 1 WHERE test_id = NEW.test_id;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE tests SET questions_count = questions_count - 1 WHERE test_id = OLD.test_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_questions ON test_questions;
CREATE TRIGGER trigger_update_questions
AFTER INSERT OR DELETE ON test_questions
FOR EACH ROW EXECUTE FUNCTION update_questions_count();

-- 3. Автозавершение теста при ответе на все вопросы
CREATE OR REPLACE FUNCTION check_test_completion()
RETURNS TRIGGER AS $$
DECLARE
    total_questions INT;
    answered_questions INT;
    test_id_var INT;
    result_id_var INT;
BEGIN
    SELECT tq.test_id INTO test_id_var
    FROM test_questions tq WHERE tq.question_id = NEW.question_id;

    SELECT tr.result_id INTO result_id_var
    FROM test_results tr
    WHERE tr.student_id = NEW.student_id AND tr.test_id = test_id_var;

    SELECT questions_count INTO total_questions
    FROM tests WHERE test_id = test_id_var;

    SELECT COUNT(DISTINCT sa.question_id) INTO answered_questions
    FROM student_answers sa
    JOIN test_questions tq ON tq.question_id = sa.question_id
    WHERE sa.student_id = NEW.student_id AND tq.test_id = test_id_var;

    IF answered_questions >= total_questions AND total_questions > 0 THEN
        UPDATE test_results
        SET status = 'завершено', completion_date = CURRENT_TIMESTAMP
        WHERE result_id = result_id_var;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_test_completion ON student_answers;
CREATE TRIGGER trigger_test_completion
AFTER INSERT ON student_answers
FOR EACH ROW EXECUTE FUNCTION check_test_completion();

-- 4. Автосоздание записи test_results при первом ответе
CREATE OR REPLACE FUNCTION create_test_record()
RETURNS TRIGGER AS $$
DECLARE
    test_id_var INT;
    record_exists BOOLEAN;
BEGIN
    SELECT test_id INTO test_id_var
    FROM test_questions WHERE question_id = NEW.question_id;

    SELECT EXISTS (
        SELECT 1 FROM test_results
        WHERE student_id = NEW.student_id AND test_id = test_id_var
    ) INTO record_exists;

    IF NOT record_exists THEN
        INSERT INTO test_results (student_id, test_id, start_date, status)
        VALUES (NEW.student_id, test_id_var, CURRENT_TIMESTAMP, 'в_процессе');
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_create_test_record ON student_answers;
CREATE TRIGGER trigger_create_test_record
BEFORE INSERT ON student_answers
FOR EACH ROW EXECUTE FUNCTION create_test_record();

-- 5. Запрет повторных ответов на вопрос
CREATE OR REPLACE FUNCTION prevent_duplicate_answers()
RETURNS TRIGGER AS $$
DECLARE
    answer_exists BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM student_answers
        WHERE student_id = NEW.student_id AND question_id = NEW.question_id
    ) INTO answer_exists;

    IF answer_exists THEN
        RAISE EXCEPTION 'Учащийся уже ответил на этот вопрос';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_prevent_duplicates ON student_answers;
CREATE TRIGGER trigger_prevent_duplicates
BEFORE INSERT ON student_answers
FOR EACH ROW EXECUTE FUNCTION prevent_duplicate_answers();

-- 6. Валидация и установка recommendation_level при добавлении рекомендации
CREATE OR REPLACE FUNCTION calculate_match_percentage()
RETURNS TRIGGER AS $$
BEGIN
    -- Если match_percentage не передан — устанавливаем 0
    IF NEW.match_percentage IS NULL THEN
        NEW.match_percentage := 0;
    END IF;

    -- Устанавливаем уровень рекомендации на основе процента совпадения
    IF NEW.match_percentage >= 70 THEN
        NEW.recommendation_level := 1;  -- высокий
    ELSIF NEW.match_percentage >= 40 THEN
        NEW.recommendation_level := 2;  -- средний
    ELSE
        NEW.recommendation_level := 3;  -- низкий
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_calculate_match ON profession_recommendations;
CREATE TRIGGER trigger_calculate_match
BEFORE INSERT ON profession_recommendations
FOR EACH ROW EXECUTE FUNCTION calculate_match_percentage();
