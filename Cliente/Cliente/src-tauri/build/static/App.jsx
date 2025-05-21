import { useEffect, useState } from "react";
import axios from "axios";

function App() {
    const [seasons, setSeasons] = useState([]);
    const [events, setEvents] = useState([]);
    const [competitions, setCompetitions] = useState([]);
    const [links, setLinks] = useState([]);
    const [selected, setSelected] = useState({ season: "", event: "", competition: "" });
    const [html, setHtml] = useState("");

    useEffect(() => {
        axios.get("http://localhost:8080/api/seasons").then((res) => setSeasons(res.data));
    }, []);

    useEffect(() => {
        if (selected.season) {
            axios.get("http://localhost:8080/api/events", { params: { season: selected.season } })
                .then((res) => setEvents(res.data));
        }
    }, [selected.season]);

    useEffect(() => {
        if (selected.season && selected.event) {
            axios.get("http://localhost:8080/api/competitions", { params: { season: selected.season, event: selected.event } })
                .then((res) => setCompetitions(res.data));
        }
    }, [selected.event]);

    useEffect(() => {
        if (selected.season && selected.event && selected.competition) {
            axios.get("http://localhost:8080/api/links", {
                params: {
                    season: selected.season,
                    event: selected.event,
                    competition: selected.competition,
                },
            }).then((res) => setLinks(res.data));
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
        const nombre = `${link}_barra_${selected.competition}_barra_season_${selected.season}_barra_${selected.event}`;
        axios.get(`http://localhost:8080/tabla/${nombre}`)
            .then((res) => setHtml(res.data));
    };

    return (
        <div id="root">
            <div id="form_carrera">
                <form>
                    <label htmlFor="season">Season:</label>
                    <select id="season" onChange={(e) => handleSelect("season", e.target.value)}>
                        <option value="">--</option>
                        {seasons.map((s) => (
                            <option key={s} value={s}>{s}</option>
                        ))}
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
                        <a key={link} href="#" onClick={() => handleLinkClick(link)}>
                            {link}
                        </a>
                    ))}
                </div>
                <div id="results" dangerouslySetInnerHTML={{ __html: html }}></div>
            </div>
        </div>
    );
}

export default App;
