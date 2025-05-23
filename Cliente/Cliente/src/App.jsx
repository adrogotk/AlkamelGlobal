import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/tauri";

function App() {
    const [seasons, setSeasons] = useState([]);
    const [events, setEvents] = useState([]);
    const [competitions, setCompetitions] = useState([]);
    const [links, setLinks] = useState([]);
    const [selected, setSelected] = useState({ season: "", event: "", competition: "" });
    const [html, setHtml] = useState("");

    useEffect(() => {
        invoke("getSeasons")
            .then(setSeasons)
            .catch((err) => console.error("Error al obtener seasons:", err));
    }, []);

    useEffect(() => {
        if (selected.season) {
            invoke("getEvents", { season: selected.season })
                .then(setEvents)
                .catch((err) => console.error("Error al obtener events:", err));
        }
    }, [selected.season]);

    useEffect(() => {
        if (selected.season && selected.event) {
            invoke("getCompetitions", {
                season: selected.season,
                event: selected.event
            })
                .then(setCompetitions)
                .catch((err) => console.error("Error al obtener competitions:", err));
        }
    }, [selected.event]);

    useEffect(() => {
        if (selected.season && selected.event && selected.competition) {
            invoke("getLinks", {
                season: selected.season,
                event: selected.event,
                competition: selected.competition
            })
                .then(setLinks)
                .catch((err) => console.error("Error al obtener links:", err));
        }
    }, [selected.competition]);

    const handleSelect = (field, value) => {
        setSelected((prev) => ({ ...prev, [field]: value }));
        if (field === "season") {
            setEvents([]);
            setCompetitions([]);
            setLinks([]);
        } else if (field === "event") {
            setCompetitions([]);
            setLinks([]);
        } else if (field === "competition") {
            setLinks([]);
        }
        setHtml("");
    };

    const handleLinkClick = (link) => {
        link=link.replace(/ /g, "_")
        console.log(`${link}_barra_${selected.competition}_barra_${selected.season}_barra_${selected.event}`)
        const nombre = `${link}_barra_${selected.competition}_barra_${selected.season}_barra_${selected.event}`;
        invoke("verTabla", { nombre })
            .then(setHtml)
            .catch((err) => console.error("Error al obtener tabla HTML:", err));
    };

    return (
        <div id="root">
            <div id="formSesion">
                <form>
                    <label htmlFor="season">Season:</label>
                    <select id="season" onChange={(e) => handleSelect("season", e.target.value)}>
                        <option value="">--</option>
                        {seasons.map((s) => {
                            const yearCode = s.split("_");
                            const year = yearCode.length > 1 ? yearCode[1] : s;
                            return (
                                <option key={s} value={s}>
                                    {year}
                                </option>
                            );
                        })}
                    </select><br />

                    <label htmlFor="event">Event:</label>
                    <select id="event" onChange={(e) => handleSelect("event", e.target.value)}>
                        <option value="">--</option>
                        {events.map((e) => (
                            <option key={e} value={e}>{e}</option>
                        ))}
                    </select><br />

                    <label htmlFor="competition">Competition:</label>
                    <select id="competition" onChange={(e) => handleSelect("competition", e.target.value)}>
                        <option value="">--</option>
                        {competitions.map((c) => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </select><br />
                </form>
            </div>

            <br /><br />
            <div id="session">
                <div id="documents">
                    {links.map((link) => (
                      <p><a key={link} href="#" onClick={() => handleLinkClick(link)}>
                            {link}
                        </a>        </p>

                    ))}
                </div>
                <div id="results" dangerouslySetInnerHTML={{ __html: html }}></div>
            </div>
        </div>
    );
}

export default App;
