const CONFIG = {
    iconBasePath: "/media/images/"
}, withAssetVersion = window.withAssetVersion || (e => e), SUPPORTED_LOCALES = [ "zh-TW", "en-US", "zh-CN", "th-TH", "id-ID" ];

function detectLocale() {
    const e = new URLSearchParams(window.location.search).get("lang"), t = localStorage.getItem("ro_lang"), n = document.documentElement.getAttribute("lang"), l = Array.isArray(navigator.languages)[...]
    for (const e of i) {
        if (!e) continue;
        const t = SUPPORTED_LOCALES.find(t => t.toLowerCase() === String(e).toLowerCase());
        if (t) return t;
    }
    for (const e of i) {
        if (!e) continue;
        const t = String(e).split("-")[0].toLowerCase();
        if ("zh" === t) {
            if (o("zh-TW")) return "zh-TW";
            const e = SUPPORTED_LOCALES.find(e => e.toLowerCase().startsWith("zh-"));
            if (e) return e;
        }
        if ("en" === t && o("en-US")) return "en-US";
        if (("id" === t || "in" === t) && o("id-ID")) return "id-ID";
    }
    return o("en-US") ? "en-US" : o("zh-TW") ? "zh-TW" : SUPPORTED_LOCALES[0] || "en-US";
}

// Force English-only locale for this deployment
const ACTIVE_LOCALE = "en-US";

localStorage.setItem("ro_lang", ACTIVE_LOCALE), document.documentElement.setAttribute("lang", ACTIVE_LOCALE);

const GRID_COLUMNS = 5, ICON_PATHS_URL = "data/icon_paths.json", SKILLS_INDEX_URL = `data/skills_index_${ACTIVE_LOCALE}.json`, JOB_DATA_URL = e => `data/jobs_${ACTIVE_LOCALE}/${e}.json`, JOB_SELEC[...]
    "zh-TW": "選擇職業...",
    "en-US": "Select a Target Job...",
    "zh-CN": "选择职业...",
    "th-TH": "เลือกอาชีพ..."
};

let iconPaths = null, iconPathsPromise = null;

const lastPointerPos = {
    x: null,
    y: null
};

let tooltipAnchorEl = null, tooltipAnchorKindId = null, tooltipPlacement = null, outlineRefreshFrame = 0, outlineResizeObserver = null, lastSkillModalTriggerEl = null;

const MOBILE_SKILL_PLANNER_MEDIA = "(max-width: 768px), (max-width: 1371px)", TAG_COLOR_BY_ICON = {
    icon_skilltype_01: "#A0E589",
    icon_skilltype_02: "#F6B965",
    icon_skilltype_03: "#DA9BF1",
    icon_skilltype_04: "#FF7373",
    icon_skilltype_05: "#D1B08C",
    icon_skilltype_06: "#7FD6C7",
    icon_skilltype_07: "#E8D27A",
    icon_skilltype_08: "#A0A7FF",
    icon_skilltype_09: "#E7B6C8",
    icon_skilltype_10: "#4D81AD",
    icon_skilltype_11: "#63C9F6",
    icon_skilltype_12: "#C7DBED",
    icon_skilltype_20: "#F2A45A",
    icon_skilltype_21: "#5FAED8",
    icon_skilltype_22: "#4FB3A6",
    icon_skilltype_23: "#63B85C",
    icon_skilltype_24: "#B7C2DE",
    icon_skilltype_25: "#5C79D6",
    icon_skilltype_26: "#E0625A",
    icon_skilltype_27: "#E9B73A",
    icon_skilltype_28: "#B183D6",
    icon_skilltype_29: "#E09559",
    icon_skilltype_30: "#8F6660",
    icon_skilltype_31: "#CFE3F3"
}, TAG_COLOR_FALLBACK = [ "#8b9bbf", "#3ba9ff", "#57f287", "#faa61a", "#ed4245", "#c084fc" ], SKILL_TYPE_LABELS = {
    0: "None",
    1: "Active",
    2: "Passive",
    3: "Auto-cast",
    4: "Active + Passive"
}, SKILL_ATTACK_TYPE_LABELS = {
    0: "None",
    1: "Attack",
    2: "Skill"
}, SKILL_DAMAGE_TYPE_LABELS = {
    0: "None",
    1: "Physical",
    2: "Magic",
    3: "Physical Heal",
    4: "Magic Heal"
}, SKILL_RANGE_TYPE_LABELS = {
    0: "None",
    1: "Melee",
    2: "Ranged"
}, SKILL_CAST_TYPE_LABELS = {
    0: "None",
    1: "No Target",
    2: "Target Point (Angle)",
    3: "Vector Targeting",
    4: "Target Unit",
    5: "Target Point or Unit",
    6: "Target Point (Add Angle)",
    7: "Charge"
}, SKILL_BUTTON_TYPE_LABELS = {
    0: "None",
    1: "Common",
    2: "Accumulator",
    3: "Aim"
}, TARGET_TYPE_LABELS = {
    0: "None",
    1: "Self",
    2: "Friend",
    3: "Enemy",
    4: "Team",
    5: "Master",
    6: "Follower",
    7: "Same Ancestor",
    8: "Lovers"
}, TARGET_UNIT_TYPE_LABELS = {
    0: "None",
    1: "Basic",
    2: "Player",
    3: "Pet",
    4: "Monster (Basic)",
    5: "Monster (Normal)",
    6: "Monster (Elite)",
    7: "Monster (Boss)",
    8: "Monster (MVP)",
    9: "Monster (Mini)",
    10: "Monster (Summon)",
    11: "Monster (Mechanism)",
    12: "Monster (Building)",
    13: "Building (Friend)",
    14: "Building (Enemy)"
}, ELEMENT_TYPE_LABELS = {
    0: "None",
    1: "Neutral",
    2: "Water",
    3: "Earth",
    4: "Fire",
    5: "Wind",
    6: "Poison",
    7: "Holy",
    8: "Shadow",
    9: "Ghost",
    10: "Undead"
};

function isBadSkillDisplayName(e) {
    const t = String(e || "").trim();
    return !t || !!/^skill\s+\d+$/i.test(t);
}

function resolveSkillDisplayName(e, t) {
    const n = String(t?.name || t?.skilldes || "").trim();
    return isBadSkillDisplayName(n) ? `Skill ${e}` : n;
}

function resolveJobDisplayName(e) {
    const t = String(e?.job_name || e?.name || "").trim();
    return t || `Job ${e?.job_id || ""}`;
}

function escapeHtml(e) {
    return String(e || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\"/g, "&quot;").replace(/'/g, "&#39;");
}

function formatNumber(e) {
    const t = Number(e);
    return Number.isFinite(t) ? Number.isInteger(t) ? String(t) : t.toFixed(2).replace(/\.?0+$/, "") : "";
}

function formatPercent(e) {
    const t = formatNumber(e);
    return "" === t ? "" : `${t}%`;
}

function formatList(e, t) {
    return Array.isArray(e) && 0 !== e.length ? e.map(e => {
        const n = Number(e);
        return Number.isFinite(n) ? t && t[n] ? t[n] : String(n) : null;
    }).filter(Boolean).join(", ") : "";
}

function isPassiveSkill(e) {
    return !!e && (2 === Number(e.skill_type) || (e.skill_tags || []).some(e => e && ("icon_skilltype_24" === e.icon || "被動" === e.name || "Passive" === e.name)));
}

function getPvpTrend(e, t) {
    const n = Number(e), l = Number(t);
    return Number.isFinite(n) && Number.isFinite(l) ? n > l ? '<span class="pvp-trend up">▲</span>' : n < l ? '<span class="pvp-trend down">▼</span>' : "" : "";
}

function hasNonZeroDamageStats(e) {
    return [ e.pve_percent, e.pve_flat, e.pvp_percent, e.pvp_flat ].some(e => Number.isFinite(Number(e)) && 0 !== Number(e));
}

function renderTagChips(e) {
    if (!e || !e.length) return "";
    const t = e.map(e => {
        const t = escapeHtml(e.name || "");
        if (!t) return "";
        const n = getTagColor(e);
        return `<span class="skill-tag" ${n ? `style="--tag-color: ${n}"` : "">${t}</span>`;
    }).join("");
    return t.trim() ? `<div class="skill-tags">${t}</div>` : "";
}

function getUnmetPrerequisites(e, t) {
    if (!e || !e.pre_skill || !e.pre_skill.length) return [];
    const n = [];
    for (const l of e.pre_skill) {
        const e = Number(l);
        if (!Number.isFinite(e)) continue;
        const i = Math.floor(e / 100), o = e % 100, s = t[i] || 0;
        if (s >= o) continue;
        const a = getSkillEntry(String(i)), r = a && a.skill ? resolveSkillDisplayName(i, a.skill) : `Skill ${i}`;
        n.push({
            kindId: i,
            requiredLevel: o,
            currentLevel: s,
            name: r
        });
    }
    return n;
}

const state = {
    currentJobId: 101,
    skillPoints: {},
    uniqueSkillPoints: {},
    jobPath: [ 101 ],
    targetJobId: null,
    data: null,
    skillPointsPerJob: {},
    breadcrumbs: [],
    selectedSkillKindId: null,
    restoreScrollOnRender: !1,
    scrollTargetJobId: null,
    scrollTargetSelectionJobId: null,
    selectionShownForJobs: new Set,
    jobLoadPromises: {},
    pendingRender: !1,
    locale: "en-US"
};

function makeSkillSelection(e) {
    return `skill:${String(e)}`;
}

function makeUniqueSelection(e) {
    return `unique:${String(e)}`;
}

function parseSelectionToken(e) {
    const t = String(e || "").trim();
    if (!t) return null;
    if (t.startsWith("unique:")) {
        const e = t.slice(7);
        return e ? {
            type: "unique",
            id: e
        } : null;
    }
    if (t.startsWith("skill:")) {
        const e = t.slice(6);
        return e ? {
            type: "skill",
            id: e
        } : null;
    }
    return {
        type: "skill",
        id: t
    };
}

function getCurrentUniqueSkillContext(e = state.jobPath) {
    const t = Array.isArray(e) ? e : [];
    for (let e = t.length - 1; e >= 0; e -= 1) {
        const n = state.data && state.data[t[e]], l = n && n.unique_skills;
        if (l && Object.keys(l).length) return {
            job: n,
            uniqueSkills: l
        };
    }
    return {
        job: null,
        uniqueSkills: {}
    };
}

// ... rest of original simulator.js unchanged ...

document.addEventListener("DOMContentLoaded", initSimulator);
