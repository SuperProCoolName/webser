const express = require("express");
const app = express();
const port = 3000;
const path = require("path");
const expressLayouts = require("express-ejs-layouts");

app.use(express.static("public"));
app.use(express.static(path.join(__dirname, "public")));
app.use(express.urlencoded({ extended: false }));
app.use(express.json());
app.set("view engine", "ejs");

// Подключаем layout middleware
app.use(expressLayouts);
app.set("layout", "layout"); // указываем файл layout.ejs как основной шаблон

const fetch = require("node-fetch");
// Функция получения данных о странах
async function getCountries() {
	const response = await fetch("https://restcountries.com/v3.1/all");
	const data = await response.json();
	return data.map((country) => ({
		id: country.cca3,
		name: country.name.common,
		population: country.population.toLocaleString(),
		languages: country.languages ? Object.values(country.languages) : [],
		capital: country.capital ? country.capital[0] : "Нет данных",
		area: `${country.area.toLocaleString()} км²`,
		currency: country.currencies ? Object.values(country.currencies)[0].name : "Нет данных",
		continent: country.region,
		flag: country.flags.png,
	}));
}

// Функция для получения случайных элементов из массива
function getRandomElements(array, count) {
	const shuffled = [...array].sort(() => 0.5 - Math.random());
	return shuffled.slice(0, count);
}

// Маршруты
app.get("/", async (req, res) => {
	const countries = await getCountries();
	const randomCountries = getRandomElements(countries, 3);

	res.render("index", {
		title: "Главная",
		popularCountries: randomCountries, // используем тот же параметр для совместимости с шаблоном
	});
});

app.get("/countries", async (req, res) => {
	const regionFilter = req.query.region || "";
	const countries = await getCountries();

	let filteredCountries = countries;
	if (regionFilter) {
		filteredCountries = countries.filter((country) => country.continent.toLowerCase() === regionFilter.toLowerCase());
	}

	res.render("countries", {
		title: "Список стран",
		countries: filteredCountries,
		regionFilter,
	});
});

app.get("/country/:id", async (req, res) => {
	const countries = await getCountries();
	const country = countries.find((c) => c.id === req.params.id);

	if (!country) {
		res.status(404).render("error", {
			title: "Страна не найдена",
			message: "Запрашиваемая страна не существует",
		});
		return;
	}

	res.render("country", {
		title: country.name,
		country,
	});
});

app.get("/search", async (req, res) => {
	const searchQuery = req.query.q ? req.query.q.toLowerCase() : "";
	const regionFilter = req.query.region || "";

	const countries = await getCountries();

	let filteredCountries = countries;

	// Применяем фильтр по региону
	if (regionFilter) {
		filteredCountries = filteredCountries.filter((country) => country.continent.toLowerCase() === regionFilter.toLowerCase());
	}

	// Применяем поиск по названию
	if (searchQuery) {
		filteredCountries = filteredCountries.filter((country) => country.name.toLowerCase().includes(searchQuery) || country.capital.toLowerCase().includes(searchQuery));
	}

	res.render("search", {
		title: "Результаты поиска",
		countries: filteredCountries,
		searchQuery,
		regionFilter,
	});
});

app.get("/guide", (req, res) => {
	res.render("guide", { title: "Руководство пользователя" });
});

app.use((err, req, res, next) => {
	console.error(err.stack);
	res.status(500).render("error", {
		title: "Ошибка",
		message: "Что-то пошло не так",
	});
});

app.listen(port, () => {
	console.log(`Сервер запущен на http://localhost:${port}`);
});
