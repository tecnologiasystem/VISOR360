import React, {
  useMemo,
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import "./kpiTablero.css";
import dayjs from "dayjs";
import "dayjs/locale/es";
dayjs.locale("es");
import { useQuery } from "react-query";
import { api } from "../services/api";
import {
  Select,
  DatePicker,
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
  Popconfirm,
  Upload,
  Space,
  message,
  Checkbox,
} from "antd";
import * as XLSX from "xlsx";

const { Option } = Select;

/* ------------------------------- Catálogo KPI ------------------------------ */
const META = {
  CLIENTES_TOTALES: { label: "Clientes asignados", agg: "last", fmt: "num" },
  CLIENTES_GESTIONABLES: {
    label: "Clientes con acuerdo",
    agg: "last",
    fmt: "num",
  },
  RECAUDO_Q: { label: "Recaudo a la fecha", agg: "sum", fmt: "num" },
  META: { label: "Meta", agg: "last", fmt: "money0" },

  CLIENTES_CONTACTADOS: {
    label: "Clientes contactados",
    agg: "sum",
    fmt: "num",
  },
  TICKET_CONTACTO: { label: "Ticket Promedio día", agg: "last", fmt: "money0" },

  ACUERDOS_Q: { label: "Total acuerdos", agg: "sum", fmt: "num" },
  ACUERDOS_DOLAR: { label: "Acuerdos $", agg: "sum", fmt: "money0" },
  TICKET_ACUERDOS: {
    label: "Monto Prom x Acuerdo",
    agg: "last",
    fmt: "money0",
  },

  EFECTIVIDAD: { label: "Efectividad", agg: "last", fmt: "percent2" },
  PLANTA: { label: "Planta", agg: "last", fmt: "num" },
};

const fmt = {
  num: (v) => (v == null ? "000" : Intl.NumberFormat().format(v)),
  money0: (v) =>
    v == null
      ? "$0000000"
      : Intl.NumberFormat(undefined, {
          style: "currency",
          currency: "USD",
          maximumFractionDigits: 0,
        }).format(v),
  percent2: (v) =>
    v == null
      ? "0%"
      : Intl.NumberFormat(undefined, {
          style: "percent",
          maximumFractionDigits: 2,
        }).format(v),
};

/* ------------------------------ Helpers calendario ------------------------- */
function workdaysInMonth(d) {
  const start = d.startOf("month"),
    end = d.endOf("month");
  let n = 0;
  for (
    let cur = start;
    cur.isBefore(end) || cur.isSame(end, "day");
    cur = cur.add(1, "day")
  ) {
    const dow = cur.day();
    if (dow !== 0 && dow !== 6) n++;
  }
  return n;
}
function workIndexUpTo(d) {
  const start = d.startOf("month");
  let n = 0;
  for (
    let cur = start;
    cur.isBefore(d) || cur.isSame(d, "day");
    cur = cur.add(1, "day")
  ) {
    const dow = cur.day();
    if (dow !== 0 && dow !== 6) n++;
  }
  return n;
}

/* ------------------------- Parse helpers para Excel ------------------------ */
function parseNumberFromString(raw) {
  if (raw == null) return null;
  if (typeof raw === "number") return raw;
  let s = String(raw).trim();
  s = s.replace(/\s/g, "");
  s = s.replace(/\$/g, "");
  if (s.match(/^[0-9]{1,3}([.,][0-9]{3})*[,\.]?[0-9]*$/)) {
    if (s.includes(".") && s.includes(",")) {
      s = s.replace(/\./g, "");
      s = s.replace(/,/g, ".");
    } else if (s.includes(".") && !s.includes(",")) {
      s = s.replace(/\./g, "");
    } else {
      s = s.replace(/,/g, "");
    }
  } else {
    s = s.replace(/[^\d\.\-]/g, "");
  }
  const n = parseFloat(s);
  return Number.isFinite(n) ? n : null;
}

const LABEL_TO_KPI = {
  "Clientes Totales": "CLIENTES_TOTALES",
  "Clientes Gestionables": "CLIENTES_GESTIONABLES",
  "Clientes Gestionados": "CLIENTES_GESTIONABLES",
  "Recaudo Q": "RECAUDO_Q",
  Recaudo: "RECAUDO_Q",
  Meta: "META",
  "Clientes Contactados": "CLIENTES_CONTACTADOS",
  "Contacto $": "CLIENTES_CONTACTADOS",
  "Ticket de Contacto": "TICKET_CONTACTO",
  "Acuerdos Q": "ACUERDOS_Q",
  "Acuerdos $": "ACUERDOS_DOLAR",
  Efectividad: "EFECTIVIDAD",
};

/* -------------------------------- Component -------------------------------- */
export default function KpiGestion() {
  const [mainTab, setMainTab] = useState("dashboard"); // 'dashboard' | 'admin'
  const [activeTab, setActiveTab] = useState("actual");
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadCandidateFile, setUploadCandidateFile] = useState(null);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedUploadAreas, setSelectedUploadAreas] = useState([]);

  const now = useMemo(() => dayjs(), []);
  const refMonth = useMemo(
    () => ({
      mes1: now.subtract(2, "month").startOf("month"),
      mes2: now.subtract(1, "month").startOf("month"),
      actual: now.startOf("month"),
    }),
    [now]
  );

  /* ---------- dashboard state ---------- */
  const [monthState, setMonthState] = useState(refMonth.actual);
  const [areaId, setAreaId] = useState(null);
  useEffect(
    () => setMonthState(refMonth[activeTab] ?? refMonth.actual),
    [activeTab, refMonth]
  );

  /* ---------- shared queries ---------- */
  const { data: areas = [] } = useQuery(
    ["areas"],
    () => api.get("/areas/").then((r) => r.data),
    { staleTime: 60000 }
  );

  useEffect(() => {
    if (!areaId && areas && areas.length > 0) {
      const firstId = areas[0].idArea ?? areas[0].id ?? areas[0].areaId ?? null;
      if (firstId) setAreaId(firstId);
    }
  }, [areas, areaId]);

  const resolvedArea = areaId;
  const desde = monthState.startOf("month").format("YYYY-MM-DD");
  const hasta =
    activeTab === "actual"
      ? now.format("YYYY-MM-DD")
      : monthState.endOf("month").format("YYYY-MM-DD");
  const periodo = monthState.format("YYYY-MM");

  const { data: kpiDefs = [], refetch: refetchDefs } = useQuery(
    ["kpi/definiciones"],
    () => api.get("/kpi/definiciones").then((r) => r.data),
    { staleTime: 60000 }
  );

  const { data: valoresRaw = [], refetch: refetchValores } = useQuery(
    ["kpi/valores", resolvedArea, desde, hasta],
    async () => {
      if (!resolvedArea) return [];
      const r = await api.get("/kpi/valores", {
        params: { areaid: resolvedArea, desde, hasta },
      });
      return r.data || [];
    },
    { enabled: !!resolvedArea }
  );

  const { data: metas = [], refetch: refetchMetas } = useQuery(
    ["kpi/metas", resolvedArea, periodo],
    async () => {
      if (!resolvedArea) return [];
      try {
        const r = await api.get("/kpi/metas", {
          params: { areaid: resolvedArea, periodo },
        });
        return r.data || [];
      } catch {
        return [];
      }
    },
    { enabled: !!resolvedArea }
  );

  const { data: asignaciones = [], refetch: refetchAsignaciones } = useQuery(
    ["kpi/asignaciones", resolvedArea],
    async () => {
      try {
        const r = await api.get("/kpi/asignaciones", {
          params: { areaid: resolvedArea, top: 200 },
        });
        return r.data || [];
      } catch {
        return [];
      }
    },
    { staleTime: 60000, enabled: !!resolvedArea }
  );

  /* ------------------ Normalize & aggregations (dashboard) ------------------ */
  const valores = useMemo(() => {
    const defMap = Object.fromEntries(
      (kpiDefs || []).map((d) => [d.KPIID, d.Codigo])
    );
    return (valoresRaw || []).map((item) => {
      const code = item.KPI_Codigo || defMap[item.KPIID] || null;
      const raw = item.FechaMedicion || item.fechaMedicion;
      const iso = raw ? dayjs(raw).format("YYYY-MM-DD") : null;
      return { ...item, KPI_Codigo: code, FechaMedicion: iso };
    });
  }, [valoresRaw, kpiDefs]);

  const metaByCode = useMemo(() => {
    const m = {};
    (metas || []).forEach((x) => {
      m[x.KPI_Codigo || x.Codigo] = Number(x.ValorMeta ?? x.Valor ?? 0) || 0;
    });
    return m;
  }, [metas]);

  const mtd = useMemo(() => {
    const byCode = {};
    for (const r of valores) {
      const code = r.KPI_Codigo;
      const spec = META[code];
      if (!spec) continue;
      const v = Number(r.Valor) || 0;
      if (spec.agg === "sum") {
        byCode[code] = (byCode[code] || 0) + v;
      } else if (spec.agg === "last") {
        const key = r.FechaMedicion;
        const ts = key ? dayjs(key).valueOf() : 0;
        const cur = byCode[code];
        if (!cur || (cur._ts || 0) < ts) byCode[code] = { _ts: ts, _v: v };
      }
    }
    Object.keys(byCode).forEach((code) => {
      if (META[code]?.agg === "last") byCode[code] = byCode[code]._v ?? 0;
    });
    if (byCode.TICKET_ACUERDOS == null) {
      const q = byCode.ACUERDOS_Q || 0;
      const $ = byCode.ACUERDOS_DOLAR || 0;
      if (q > 0 && $ > 0) byCode.TICKET_ACUERDOS = $ / q;
    }
    return byCode;
  }, [valores]);

  const acuerdosPorDiaMap = useMemo(() => {
    const acc = {};
    (valores || [])
      .filter((v) => v.KPI_Codigo === "ACUERDOS_Q")
      .forEach((v) => {
        const iso = v.FechaMedicion;
        if (!iso) return;
        acc[iso] = (acc[iso] || 0) + (Number(v.Valor) || 0);
      });
    return acc;
  }, [valores]);

  /* ----------------- selected area object (used later) ----------------- */
  const selectedAreaObj = useMemo(() => {
    if (!areas || !areaId) return null;
    return areas.find((a) => (a.idArea ?? a.id ?? a.areaId) == areaId) ?? null;
  }, [areas, areaId]);

  // Derived KPIs (añadir)
  const plantaValue = mtd.PLANTA ?? null; // number or null
  const promedioContactosPorHora =
    mtd.CLIENTES_CONTACTADOS != null
      ? Math.round(mtd.CLIENTES_CONTACTADOS / 8)
      : null;

  const promAcuerdosPorAsesorDia =
    mtd.ACUERDOS_Q != null && plantaValue
      ? Math.round(mtd.ACUERDOS_Q / plantaValue)
      : null;

  /* ------------------- OVERRIDE desde Excel (preview local) -------------------- */
  const [excelOverride, setExcelOverride] = useState(null);

  async function handleExcelFileLocalParse(file) {
    try {
      const data = await file.arrayBuffer();
      const workbook = XLSX.read(data);
      const sheet = workbook.Sheets[workbook.SheetNames[0]];
      const json = XLSX.utils.sheet_to_json(sheet, { header: 1, raw: false });

      let areaName = null;
      let periodMaybe = null;
      const values = {};
      const acuerdosPorDiaFromExcel = {};

      if (json.length > 0 && json[0].length > 0) {
        const r0c0 = (json[0][0] || "").toString().trim();
        if (r0c0 && !/mes/i.test(r0c0)) areaName = r0c0;
      }

      for (let r = 0; r < json.length; r++) {
        const row = json[r];
        if (!row || row.length === 0) continue;
        for (let c = 0; c < row.length; c++) {
          const cell = (row[c] || "").toString().trim();
          if (/^mes$/i.test(cell) && row[c + 1])
            periodMaybe = (row[c + 1] || "").toString().trim();
        }
        const label = (row[0] || "").toString().trim();
        const cand1 = row[1];
        const cand2 = row[row.length - 1];
        let rawValue = null;
        if (label) {
          if (cand1 != null && String(cand1).trim() !== "") rawValue = cand1;
          else if (cand2 != null && String(cand2).trim() !== "")
            rawValue = cand2;
          const key = Object.keys(LABEL_TO_KPI).find(
            (k) => k.toLowerCase() === label.toLowerCase()
          );
          const kpi = key ? LABEL_TO_KPI[key] : LABEL_TO_KPI[label];
          if (kpi && rawValue != null) {
            const n = parseNumberFromString(rawValue);
            if (n != null) values[kpi] = n;
          } else {
            const small = label.toLowerCase();
            if (small.includes("clientes") && small.includes("tot")) {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.CLIENTES_TOTALES = n;
            }
            if (small.includes("clientes") && small.includes("gestion")) {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.CLIENTES_GESTIONABLES = n;
            }
            if (small.includes("recaud") && rawValue != null) {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.RECAUDO_Q = n;
            }
            if (small === "meta" || small.includes("meta")) {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.META = n;
            }
            if (small.includes("acuerdos q") || small === "acuerdos q") {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.ACUERDOS_Q = n;
            }
            if (small.includes("acuerdos $") || small.includes("acuerdos")) {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.ACUERDOS_DOLAR = n;
            }
            if (small.includes("ticket") && small.includes("contacto")) {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.TICKET_CONTACTO = n;
            }
            if (small.includes("contactad")) {
              const n = parseNumberFromString(rawValue);
              if (n != null) values.CLIENTES_CONTACTADOS = n;
            }
            if (small.includes("efectividad")) {
              let n = parseNumberFromString(rawValue);
              if (n != null) {
                if (n > 1 && n <= 100) n = n / 100;
                values.EFECTIVIDAD = n;
              }
            }
          }
        }
      }

      setExcelOverride({
        areaName,
        periodMaybe,
        values,
        acuerdosPorDiaFromExcel,
        rawTable: json,
      });

      if (periodMaybe) {
        const p = periodMaybe.replace(/_/g, "-");
        let parsed = null;
        const mES = {
          ene: "01",
          feb: "02",
          mar: "03",
          abr: "04",
          may: "05",
          jun: "06",
          jul: "07",
          ago: "08",
          sep: "09",
          oct: "10",
          nov: "11",
          dic: "12",
        };
        const m = p.toLowerCase();
        const mDash = m.split("-");
        if (mDash.length === 2 && mES[mDash[0].slice(0, 3)]) {
          const yy = `20${mDash[1].padStart(2, "0")}`;
          const mm = mES[mDash[0].slice(0, 3)];
          parsed = dayjs(`${yy}-${mm}-01`);
        } else if (/^\d{4}[-/]\d{2}/.test(p)) parsed = dayjs(p);
        else if (/^[a-z]{3,}/i.test(p))
          parsed = dayjs(p, ["MMM-YY", "MMMM-YY", "MMMM YYYY", "MMM YYYY"]);
        if (parsed && parsed.isValid()) setMonthState(parsed.startOf("month"));
      }
      message.success("Preview generado del Excel (local).");
    } catch (err) {
      console.error("Error parseando Excel:", err);
      message.error("Error leyendo Excel. Revisa formato.");
    }
  }

  async function uploadExcelToBackend(file, areaIds = null) {
    try {
      const fd = new FormData();
      fd.append("file", file);

      const areaIdsToSend =
        Array.isArray(areaIds) && areaIds.length > 0
          ? areaIds
          : Array.isArray(selectedUploadAreas) && selectedUploadAreas.length > 0
          ? selectedUploadAreas
          : null;

      if (areaIdsToSend) {
        fd.append("area_ids", JSON.stringify(areaIdsToSend));
      }

      const previewRes = await api.post(
        "/kpi/valores/upload_verbose?procesar=false",
        fd,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      console.log("Preview response:", previewRes.data);
      if (previewRes?.data?.preview) {
        message.info(
          `Preview: ${
            previewRes.data.preview.ok ?? previewRes.data.preview.ok
          } OK / ${
            previewRes.data.preview.errors ?? previewRes.data.preview.errors
          } ERR`
        );
      } else {
        message.info("Preview recibido del backend.");
      }

      const procRes = await api.post(
        "/kpi/valores/upload_verbose?procesar=true",
        fd,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );
      console.log("Process response:", procRes.data);
      message.success(
        "Import OK. Procesados=" +
          (procRes.data.sp_result?.Procesados ??
            procRes.data.Procesados ??
            procRes.data.procesados ??
            "n/a")
      );

      refetchValores();
      refetchMetas();
      refetchAsignaciones();
    } catch (e) {
      console.error("Error importando excel al backend:", e);
      message.error(
        "Error importando Excel: " + (e?.response?.data?.detail || e.message)
      );
    }
  }

  /* ------------------- computedData (dashboard) -------------------- */
  const prodDays = workdaysInMonth(monthState);
  const workIdx = workIndexUpTo(
    activeTab === "actual" ? now : monthState.endOf("month")
  );
  const daysLeft = Math.max(0, prodDays - workIdx);

  const recaudoActual = mtd.RECAUDO_Q ?? null;
  const metaMes = metaByCode.META ?? null;
  const esperadoAcum = metaMes != null ? metaMes * (workIdx / prodDays) : null;
  const porcCumpl =
    metaMes && recaudoActual != null && metaMes !== 0
      ? recaudoActual / metaMes
      : null;
  const desviacion =
    esperadoAcum != null && recaudoActual != null
      ? recaudoActual - esperadoAcum
      : null;

  const contactados = mtd.CLIENTES_CONTACTADOS ?? null;
  const base = mtd.CLIENTES_GESTIONABLES ?? null;
  const pctBase = contactados != null && base ? contactados / base : null;

  const acuerdosQ = mtd.ACUERDOS_Q ?? null;
  const ticketA = mtd.TICKET_ACUERDOS ?? null;

  const computedData = useMemo(() => {
    // base numbers (prefer excel override values when present)
    const vOverride = excelOverride?.values || null;
    const clientesContactadosNum =
      (vOverride?.CLIENTES_CONTACTADOS ?? mtd.CLIENTES_CONTACTADOS ?? 0) || 0;
    const acuerdosQNum = (vOverride?.ACUERDOS_Q ?? mtd.ACUERDOS_Q ?? 0) || 0;

    // resolve PLANTA
    const plantaCandidate =
      (vOverride && (Number(vOverride.PLANTA) || null)) ||
      (selectedAreaObj &&
        (Number(selectedAreaObj.PLANTA) ||
          Number(selectedAreaObj.Planta) ||
          Number(selectedAreaObj.planta) ||
          null)) ||
      Number(mtd.PLANTA) ||
      null;

    const planta = Number.isFinite(Number(plantaCandidate))
      ? Number(plantaCandidate)
      : null;

    // averages
    const promedioContactosNum = clientesContactadosNum / 8;
    const promAcuerdosAsesorNum =
      planta && planta > 0 ? acuerdosQNum / planta : null;

    // projection logic for ACUERDOS_Q vs its meta (if exists)
    const metaAcuerdos = metaByCode.ACUERDOS_Q ?? metaByCode.ACUERDOS ?? null;
    const loQueLlevo = acuerdosQNum;
    const remaining =
      metaAcuerdos != null ? Math.max(0, metaAcuerdos - loQueLlevo) : null;
    const neededPerDay =
      remaining != null && daysLeft > 0 ? remaining / daysLeft : null;
    const projectedIfPaceContinues =
      workIdx > 0 ? (loQueLlevo / workIdx) * Math.max(0, daysLeft) : null;

    // helpers
    const fmtMaybeNum = (n) => (n == null ? "000" : fmt.num(Math.round(n)));
    const fmtMaybeMoney = (n) =>
      n == null ? "$0000000" : fmt.money0(Math.round(n));

    // acuerdos por dia series (for timeline)
    const daysSeries = (() => {
      if (excelOverride && excelOverride.acuerdosPorDiaFromExcel) {
        const arr = Object.entries(excelOverride.acuerdosPorDiaFromExcel).map(
          ([iso, val]) => {
            const d = dayjs(iso);
            const dow = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"][
              d.day() === 0 ? 6 : d.day() - 1
            ];
            return {
              val: fmt.num(val),
              valNum: val,
              dow,
              dd: d.format("DD"),
              iso,
            };
          }
        );
        return arr;
      }
      const days = [];
      const start = monthState.startOf("month");
      const end = monthState.endOf("month");
      for (
        let d = start;
        d.isBefore(end) || d.isSame(end, "day");
        d = d.add(1, "day")
      ) {
        const iso = d.format("YYYY-MM-DD");
        const dow = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"][
          d.day() === 0 ? 6 : d.day() - 1
        ];
        const valNum = acuerdosPorDiaMap[iso] ?? 0;
        days.push({
          valNum,
          val: fmt.num(valNum),
          dow,
          dd: d.format("DD"),
          iso,
        });
      }
      return days;
    })();

    return {
      clientesAsignados: fmt.num(mtd.CLIENTES_TOTALES ?? null),
      clientesConAcuerdo: fmt.num(mtd.CLIENTES_GESTIONABLES ?? null),
      recaudo: fmt.num(recaudoActual),
      meta: fmt.money0(metaMes),
      porcCump: fmt.percent2(porcCumpl),
      desviacion: fmt.num(Math.round(desviacion ?? 0)),
      desviacionPorc: "00%",
      clientesContactados: fmt.num(contactados),
      promedioContactos: fmtMaybeNum(promedioContactosNum),
      capacity: planta != null ? fmt.num(planta) : "000",
      ticketPromedio: fmt.money0(mtd.TICKET_CONTACTO ?? null),
      totalAcuerdos: fmt.num(acuerdosQ),
      montoPromAcuerdo: fmt.money0(ticketA),
      promAcuerdosAsesor:
        promAcuerdosAsesorNum != null
          ? fmtMaybeNum(promAcuerdosAsesorNum)
          : "000",
      // proyecciones específicas para ACUERDOS_Q
      proyeccionAcuerdos:
        neededPerDay != null ? fmt.num(Math.round(neededPerDay)) : "000",
      vsAcuerdos:
        projectedIfPaceContinues != null
          ? fmt.num(Math.round(projectedIfPaceContinues))
          : "000",
      // raw numeric projection values (useful for tooltip or detail if needed)
      __raw: {
        metaAcuerdos,
        loQueLlevo,
        remaining,
        neededPerDay,
        projectedIfPaceContinues,
      },
      acuerdosPorDia: daysSeries,
      efectividad: fmt.percent2(mtd.EFECTIVIDAD ?? null),
    };
  }, [
    excelOverride,
    mtd,
    monthState,
    acuerdosPorDiaMap,
    recaudoActual,
    metaMes,
    porcCumpl,
    desviacion,
    contactados,
    acuerdosQ,
    ticketA,
    activeTab,
    now,
    selectedAreaObj,
    metaByCode,
    workIdx,
    daysLeft,
  ]);

  const campaignName =
    excelOverride?.areaName ??
    selectedAreaObj?.descripcionCampana ??
    selectedAreaObj?.descripcion ??
    selectedAreaObj?.nombreArea ??
    selectedAreaObj?.name ??
    "NPL";

  /* ------------------ Timeline scroll handlers ------------------ */
  /* ------------------ Timeline scroll handlers ------------------ */
  const timelineRef = useRef(null);
  const scrollTimeline = useCallback((amount) => {
    const node = timelineRef.current;
    if (!node) return;
    node.scrollBy({ left: amount, behavior: "smooth" });
  }, []);

  // --- usamos listener nativo para wheel con passive:false para poder preventDefault ---
  useEffect(() => {
    const node = timelineRef.current;
    if (!node) return;

    const wheelHandler = (e) => {
      // evitamos scroll de la página y convertimos wheel en scroll horizontal
      // dejamos el preventDefault porque aquí SI registramos passive: false
      e.preventDefault();
      node.scrollLeft += e.deltaY * 1.4;
    };

    node.addEventListener("wheel", wheelHandler, { passive: false });

    return () => {
      node.removeEventListener("wheel", wheelHandler, { passive: false });
    };
  }, []); // empty deps -> attach once

  // Los handlers de drag/touch se mantienen igual (no usan preventDefault)
  const isDragging = useRef(false);
  const dragStartX = useRef(0);
  const dragStartScroll = useRef(0);

  function onDragStart(e) {
    isDragging.current = true;
    dragStartX.current = e.pageX ?? (e.touches && e.touches[0].pageX) ?? 0;
    dragStartScroll.current = timelineRef.current?.scrollLeft ?? 0;
    timelineRef.current?.classList.add("is-dragging");
  }
  function onDragMove(e) {
    if (!isDragging.current) return;
    const x = e.pageX ?? (e.touches && e.touches[0].pageX) ?? 0;
    const dx = x - dragStartX.current;
    if (timelineRef.current)
      timelineRef.current.scrollLeft = dragStartScroll.current - dx;
  }
  function onDragEnd() {
    isDragging.current = false;
    if (timelineRef.current)
      timelineRef.current.classList.remove("is-dragging");
  }

  /* ----------------- Admin helpers: ensure asignacion + create meta ----------------- */
  async function ensureAsignacion(KPIID, AreaID) {
    try {
      const r = await api.get("/kpi/asignaciones", {
        params: { kpiid: KPIID, areaid: AreaID, top: 10 },
      });
      const arr = r.data || [];
      if (arr.length > 0)
        return arr[0].KPIAsignacionID ?? arr[0].id ?? arr[0].Id;
    } catch (e) {
      /* ignore */
    }

    const payloadAsign = { KPIID, AreaID, Activo: 1 };
    const r2 = await api.post("/kpi/asignaciones", payloadAsign);
    const created = r2.data || r2;
    await refetchAsignaciones();
    return created.KPIAsignacionID ?? created.id ?? created.Id;
  }

  async function ensureAsignacionAndCreateMeta({
    KPI_Codigo,
    AreaID,
    PeriodoMoment,
    ValorMeta,
  }) {
    const kpiDef = (kpiDefs || []).find((k) => k.Codigo === KPI_Codigo);
    if (!kpiDef) throw new Error("KPI no encontrado: " + KPI_Codigo);
    const KPIID = kpiDef.KPIID;

    let KPIAsignacionID = null;
    try {
      const r = await api.get("/kpi/asignaciones", {
        params: { kpiid: KPIID, areaid: AreaID, top: 10 },
      });
      const as = r.data || [];
      KPIAsignacionID = (as[0] && (as[0].KPIAsignacionID ?? as[0].id)) || null;
    } catch (e) {}

    if (!KPIAsignacionID) {
      const payloadAsign = { KPIID, AreaID, Activo: 1 };
      const r = await api.post("/kpi/asignaciones", payloadAsign);
      const created = r.data || r;
      KPIAsignacionID =
        created.KPIAsignacionID ?? created.Id ?? created.id ?? null;
      if (!KPIAsignacionID)
        throw new Error("No se obtuvo KPIAsignacionID al crear asignación");
      await refetchAsignaciones();
    }

    const inicio = PeriodoMoment.startOf("month").format("YYYY-MM-DD");
    const fin = PeriodoMoment.endOf("month").format("YYYY-MM-DD");
    const body = {
      KPIAsignacionID,
      PeriodoInicio: inicio,
      PeriodoFin: fin,
      ValorMeta: Number(Number(ValorMeta).toFixed(2)),
      Granularidad: "mensual",
    };
    const res = await api.post("/kpi/metas", body);
    await refetchMetas();
    return res.data || res;
  }

  /* ----------------- Admin UI state (modals/forms) ----------------- */
  const [defModalOpen, setDefModalOpen] = useState(false);
  const [editingDef, setEditingDef] = useState(null);
  const [formDef] = Form.useForm();

  const [metaModalOpen, setMetaModalOpen] = useState(false);
  const [formMeta] = Form.useForm();

  const [assignModalOpen, setAssignModalOpen] = useState(false);
  const [formAssign] = Form.useForm();

  // Manual value modal
  const [valModalOpen, setValModalOpen] = useState(false);
  const [formVal] = Form.useForm();

  /* ----------------- Admin operations ----------------- */
  async function createKpiDef(payload) {
    const res = await api.post("/kpi/definiciones", payload);
    await refetchDefs();
    message.success("KPI creado");
    return res.data || res;
  }
  async function updateKpiDef(kpiid, payload) {
    const res = await api.put(`/kpi/definiciones/${kpiid}`, payload);
    await refetchDefs();
    message.success("KPI actualizado");
    return res.data || res;
  }
  async function deleteKpiDef(kpiid) {
    await api.delete(`/kpi/definiciones/${kpiid}`);
    await refetchDefs();
    message.success("KPI eliminado");
  }

  /* ----------------- Columns ----------------- */
  const defsColumns = [
    { title: "Código", dataIndex: "Codigo", key: "Codigo" },
    { title: "Nombre", dataIndex: "Nombre", key: "Nombre" },
    { title: "Unidad", dataIndex: "Unidad", key: "Unidad" },
    { title: "Perspectiva", dataIndex: "Perspectiva", key: "Perspectiva" },
    {
      title: "Activo",
      dataIndex: "Activo",
      key: "Activo",
      render: (v) => (v ? "Sí" : "No"),
    },
    {
      title: "Acciones",
      key: "actions",
      render: (_, row) => (
        <Space>
          <Button
            size="small"
            onClick={() => {
              setEditingDef(row);
              formDef.setFieldsValue({
                Codigo: row.Codigo,
                Nombre: row.Nombre,
                Descripcion: row.Descripcion,
                Unidad: row.Unidad,
                TipoCalculo: row.TipoCalculo,
                Perspectiva: row.Perspectiva,
                AreaID: row.AreaID,
                Peso: row.Peso,
                Activo: row.Activo,
              });
              setDefModalOpen(true);
            }}
          >
            Edit
          </Button>
          <Popconfirm
            title="Eliminar KPI?"
            onConfirm={() => deleteKpiDef(row.KPIID)}
          >
            <Button danger size="small">
              Del
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const asignColumns = [
    { title: "ID Asign", dataIndex: "KPIAsignacionID", key: "KPIAsignacionID" },
    {
      title: "KPIID",
      dataIndex: "KPIID",
      key: "KPIID",
      render: (v) => kpiDefs.find((k) => k.KPIID === v)?.Codigo ?? v,
    },
    {
      title: "Area",
      dataIndex: "AreaID",
      key: "AreaID",
      render: (v) => {
        const a = areas.find((ar) => (ar.idArea ?? ar.id ?? ar.areaId) == v);
        return a
          ? `${a.idArea ?? a.id ?? a.areaId} - ${
              a.nombreArea ?? a.nombre ?? a.name
            }`
          : v;
      },
    },
    {
      title: "Activo",
      dataIndex: "Activo",
      key: "Activo",
      render: (v) => (v ? "Sí" : "No"),
    },
    {
      title: "Acciones",
      key: "actions",
      render: (_, row) => (
        <Space>
          <Popconfirm
            title="Eliminar asignación?"
            onConfirm={async () => {
              await api.delete(`/kpi/asignaciones/${row.KPIAsignacionID}`);
              message.success("Asignación eliminada");
              refetchAsignaciones();
            }}
          >
            <Button danger size="small">
              Del
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const metasColumns = [
    { title: "MetaID", dataIndex: "MetaAsignID", key: "MetaAsignID" },
    {
      title: "KPIAsignacionID",
      dataIndex: "KPIAsignacionID",
      key: "KPIAsignacionID",
    },
    {
      title: "PeriodoInicio",
      dataIndex: "PeriodoInicio",
      key: "PeriodoInicio",
    },
    { title: "PeriodoFin", dataIndex: "PeriodoFin", key: "PeriodoFin" },
    {
      title: "ValorMeta",
      dataIndex: "ValorMeta",
      key: "ValorMeta",
      render: (v) => (v == null ? "" : Number(v).toFixed(2)),
    },
  ];

  /* ----------------- Handlers for modals ----------------- */
  async function onDefModalOk() {
    try {
      const values = await formDef.validateFields();
      if (editingDef) {
        await updateKpiDef(editingDef.KPIID, values);
        setEditingDef(null);
      } else {
        await createKpiDef(values);
      }
      formDef.resetFields();
      setDefModalOpen(false);
    } catch (e) {
      message.error("Error guardando definición: " + (e?.message || e));
    }
  }
  function onDefModalCancel() {
    setEditingDef(null);
    formDef.resetFields();
    setDefModalOpen(false);
  }

  async function onAssignModalOk() {
    try {
      const values = await formAssign.validateFields();
      await api.post("/kpi/asignaciones", values);
      message.success("Asignación creada");
      formAssign.resetFields();
      setAssignModalOpen(false);
      refetchAsignaciones();
    } catch (e) {
      message.error("Error creando asignación: " + (e?.message || e));
    }
  }
  function onAssignModalCancel() {
    formAssign.resetFields();
    setAssignModalOpen(false);
  }

  async function onMetaModalOk() {
    try {
      const values = await formMeta.validateFields();
      const PeriodoMoment = values.Periodo;
      await ensureAsignacionAndCreateMeta({
        KPI_Codigo: values.KPI_Codigo,
        AreaID: values.AreaID,
        PeriodoMoment,
        ValorMeta: values.ValorMeta,
      });
      formMeta.resetFields();
      setMetaModalOpen(false);
      message.success("Meta creada");
    } catch (e) {
      message.error("Error creando meta: " + (e?.message || e));
    }
  }
  function onMetaModalCancel() {
    formMeta.resetFields();
    setMetaModalOpen(false);
  }

  /* ---------------- Manual value form handler ----------------- */
  async function onValModalOk() {
    try {
      const vals = await formVal.validateFields();
      const rows = vals.rows || [];
      const targetAreas = vals.targetAreas || [];
      const fecha = vals.Fecha;

      if (!fecha || !fecha.isValid()) throw new Error("Fecha inválida");
      if (!Array.isArray(targetAreas) || targetAreas.length === 0)
        throw new Error("Selecciona al menos un área");
      if (!Array.isArray(rows) || rows.length === 0)
        throw new Error("Agrega al menos una fila con KPI y valor");

      const FechaMedicion = fecha.format("YYYY-MM-DD");

      const requests = [];
      for (const areaIdSel of targetAreas) {
        for (const row of rows) {
          const kpiDef = kpiDefs.find((k) => k.Codigo === row.KPI_Codigo);
          if (!kpiDef) {
            throw new Error(`KPI no encontrado: ${row.KPI_Codigo}`);
          }
          const KPIID = kpiDef.KPIID;

          const payload = {
            KPIID,
            AreaID: areaIdSel,
            FechaMedicion,
            Valor: Number(row.Valor),
            Fuente: null,
            RunID: null,
            UsuarioID: null,
            KPIAsignacionID: null,
          };

          requests.push(api.post("/kpi/valores", payload));
        }
      }

      const settled = await Promise.allSettled(requests);

      const succ = settled.filter((r) => r.status === "fulfilled").length;
      const fail = settled.length - succ;

      if (succ > 0) message.success(`Insertados: ${succ}`);
      if (fail > 0) message.error(`Errores: ${fail} (ver consola)`);

      formVal.resetFields();
      setValModalOpen(false);
      refetchValores();
    } catch (e) {
      console.error("Error insertando valores múltiples:", e);
      const detail = e?.response?.data?.detail || e?.message || String(e);
      message.error("Error guardando valores: " + detail);
    }
  }

  /* ------------------ Upload props (antd Upload) ------------------ */
  const uploadProps = {
    accept: ".xlsx,.xls,.csv",
    beforeUpload: (file) => {
      handleExcelFileLocalParse(file);
      setUploadCandidateFile(file);
      setSelectedFile(file);
      setUploadModalOpen(true);
      return false; // prevent automatic upload
    },
    showUploadList: false,
  };

  /* ------------------ Render ------------------ */
  function renderDashboardTab() {
    return (
      <>
        <div className="kpi-dashboard page-pad">
          <div
            className="dashboard-header"
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: 8,
            }}
          >
            <h1 className="dashboard-title">Gestión {campaignName}</h1>

            <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
              <div style={{ minWidth: 220 }}>
                <label className="field-label">Área</label>
                <Select
                  value={areaId}
                  onChange={(v) => setAreaId(v)}
                  showSearch
                  placeholder="Seleccione área"
                  style={{ width: 220 }}
                  optionFilterProp="children"
                >
                  {areas.map((a) => (
                    <Option
                      key={a.idArea ?? a.id ?? a.areaId ?? JSON.stringify(a)}
                      value={a.idArea ?? a.id ?? a.areaId}
                    >
                      {(a.idArea ?? a.id ?? a.areaId) +
                        " - " +
                        (a.nombreArea ??
                          a.nombre ??
                          a.name ??
                          a.descripcion ??
                          "Área")}
                    </Option>
                  ))}
                </Select>
              </div>

              <div>
                <label className="field-label">Mes</label>
                <DatePicker
                  picker="month"
                  value={monthState}
                  onChange={(d) => d && setMonthState(d.startOf("month"))}
                  format="MMMM YYYY"
                />
              </div>

              <div style={{ display: "flex", gap: 8, alignItems: "flex-end" }}>
                <div className="pill" style={{ background: "#e7f0ff" }}>
                  Días productivos:{" "}
                  <strong style={{ marginLeft: 8 }}>{prodDays}</strong>
                </div>
                <div className="pill" style={{ background: "#fff3e0" }}>
                  Días para cierre:{" "}
                  <strong style={{ marginLeft: 8 }}>{daysLeft}</strong>
                </div>
              </div>
            </div>

            <div className="tabs-container" style={{ marginTop: 8 }}>
              <button
                className={`tab-button ${activeTab === "mes1" ? "active" : ""}`}
                onClick={() => setActiveTab("mes1")}
              >
                Mes 1
              </button>
              <button
                className={`tab-button ${activeTab === "mes2" ? "active" : ""}`}
                onClick={() => setActiveTab("mes2")}
              >
                Mes 2
              </button>
              <button
                className={`tab-button ${
                  activeTab === "actual" ? "active" : ""
                }`}
                onClick={() => setActiveTab("actual")}
              >
                Actual
              </button>
            </div>
          </div>

          <div className="main-grid" style={{ marginTop: 18 }}>
            <div className="top-row">
              <div className="stat-card kpi-card">
                <div className="stat-label">Clientes asignados</div>
                <div className="stat-value animate-digit">
                  {computedData.clientesAsignados}
                </div>
              </div>

              <div className="stat-card kpi-card">
                <div className="stat-label">Clientes con acuerdo</div>
                <div className="stat-value animate-digit">
                  {computedData.clientesConAcuerdo}
                </div>
              </div>

              <div className="recaudo-card kpi-card">
                <div className="recaudo-main">
                  <div className="recaudo-inner">
                    <div className="recaudo-label">Recaudo a la fecha</div>
                    <div className="recaudo-value animate-digit">
                      {computedData.recaudo}
                    </div>
                  </div>
                  <div className="meta-box">
                    <div className="meta-label">Meta</div>
                    <div className="meta-value animate-digit">
                      {computedData.meta}
                    </div>
                  </div>
                </div>
                <div className="recaudo-metrics">
                  <div className="metric-item">
                    <div className="metric-label">Porc. Cump</div>
                    <div className="metric-value animate-digit">
                      {computedData.porcCump}
                    </div>
                  </div>
                  <div className="metric-item">
                    <div className="metric-label">Desviación</div>
                    <div className="metric-value animate-digit">
                      {computedData.desviacion}
                    </div>
                  </div>
                </div>
              </div>

              <div className="deviation-card kpi-card">
                <div className="deviation-label">Desviación</div>
                <div className="deviation-value animate-digit">
                  {computedData.desviacionPorc}
                </div>
              </div>
            </div>

            <div className="section-header">
              <div className="section-ribbon">
                <span>Contacto</span>
              </div>
            </div>
            <div className="stats-row five-cols">
              <div className="stat-card kpi-card">
                <div className="stat-label">Clientes contactados</div>
                <div className="stat-value animate-digit">
                  {computedData.clientesContactados}
                </div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">Porcentaje de la base</div>
                <div className="stat-value animate-digit">
                  {computedData.porcBase}
                </div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">Ticket Promedio día</div>
                <div className="stat-value animate-digit">
                  {computedData.ticketPromedio}
                </div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">
                  Promedio contactos efectivos x hora
                </div>
                <div className="stat-value animate-digit">
                  {computedData.promedioContactos}
                </div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">Capacity actual</div>
                <div className="stat-value animate-digit">
                  {computedData.capacity}
                </div>
              </div>
            </div>

            <div className="section-header">
              <div className="section-ribbon">
                <span>Acuerdos</span>
              </div>
            </div>
            <div className="stats-row four-cols">
              <div className="stat-card large kpi-card">
                <div className="stat-label">Total acuerdos</div>
                <div className="stat-value large animate-digit">
                  {computedData.totalAcuerdos}
                </div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">Monto Prom x Acuerdo</div>
                <div className="stat-value animate-digit">
                  {computedData.montoPromAcuerdo}
                </div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">Porcentaje caída de acuerdos</div>
                <div className="stat-value animate-digit">
                  {computedData.porcCaidaAcuerdos}
                </div>
              </div>
              <div className="stat-card with-vs kpi-card">
                <div className="stat-label">
                  Proyección acuerdos x día para cumplimiento
                </div>
                <div className="stat-value animate-digit">
                  {computedData.proyeccionAcuerdos}
                </div>
                <div className="vs-badge">
                  Vs <span>{computedData.vsAcuerdos}</span>
                </div>
              </div>
            </div>

            <div className="projection-pills">
              <div className="projection-pill">
                <span>Proyección acuerdos x día para cumplimiento</span>
                <span className="pill-value">
                  {computedData.proyeccionAcuerdos}
                </span>
                <span className="vs">Vs</span>
                <span className="pill-value">{computedData.vsAcuerdos}</span>
              </div>
              <div className="projection-pill">
                <span>Proyección monto x acuerdo para cumplimiento</span>
                <span className="pill-value">
                  {computedData.proyeccionMonto}
                </span>
                <span className="vs">Vs</span>
                <span className="pill-value">{computedData.vsMonto}</span>
              </div>
            </div>

            <div className="timeline-container">
              <div className="timeline-header">
                <strong>
                  Consolidado acuerdos por día - {monthState.format("MMMM")}
                </strong>
              </div>

              <div className="timeline-rail-wrapper">
                <button
                  aria-label="Izquierda"
                  className="timeline-arrow-btn left"
                  onClick={() =>
                    scrollTimeline(
                      -(timelineRef.current?.clientWidth ?? 300) * 0.8
                    )
                  }
                >
                  ‹
                </button>

                <div
                  className="timeline-track"
                  ref={timelineRef}
                  onMouseDown={onDragStart}
                  onMouseMove={onDragMove}
                  onMouseUp={onDragEnd}
                  onMouseLeave={onDragEnd}
                  onTouchStart={onDragStart}
                  onTouchMove={onDragMove}
                  onTouchEnd={onDragEnd}
                  role="list"
                  tabIndex={0}
                >
                  {computedData.acuerdosPorDia.map((day, idx) => (
                    <div key={idx} className="timeline-cell" role="listitem">
                      <div className="timeline-cell-top">{day.val}</div>
                      <div className="timeline-cell-bottom">
                        <span>{day.dow}</span>
                        <span>{day.dd}</span>
                      </div>
                    </div>
                  ))}
                </div>

                <button
                  aria-label="Derecha"
                  className="timeline-arrow-btn right"
                  onClick={() =>
                    scrollTimeline(
                      (timelineRef.current?.clientWidth ?? 300) * 0.8
                    )
                  }
                >
                  ›
                </button>
              </div>
            </div>

            <div className="section-header">
              <div className="section-ribbon">
                <span>Productividad</span>
              </div>
            </div>
            <div className="stats-row four-cols">
              <div className="stat-card kpi-card">
                <div className="stat-label">Prom. acuerdos x asesor día</div>
                <div className="stat-value">
                  {computedData.promAcuerdosAsesor}
                </div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">Porc. Cump</div>
                <div className="stat-value">{computedData.porcCumpProd}</div>
              </div>
              <div className="stat-card kpi-card">
                <div className="stat-label">Desviación</div>
                <div className="stat-value">{computedData.desviacionProd}</div>
              </div>
              <div className="effectiveness-card kpi-card">
                <div className="effectiveness-label">Efectividad</div>
                <div className="effectiveness-value">
                  {computedData.efectividad}
                </div>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

   function renderAdminTab() {
    return (
      <div className="kpi-admin-container">
        {/* Header con título y acciones principales */}
        <div className="admin-header">
          <div className="admin-title-section">
            <h1 className="admin-title">
              <span className="admin-icon">⚙️</span>
              Administración de KPIs y OKRs
            </h1>
            <p className="admin-subtitle">
              Gestiona definiciones, asignaciones, metas y valores de indicadores
            </p>
          </div>
          
          <div className="admin-actions">
            <button
              className="action-card"
              onClick={() => {
                setDefModalOpen(true);
                setEditingDef(null);
              }}
              title="Crear una nueva definición de KPI con sus propiedades básicas"
            >
              <div className="action-icon">📊</div>
              <div className="action-label">Nuevo KPI</div>
              <div className="action-description">Definir indicador</div>
            </button>

            <button
              className="action-card"
              onClick={() => setAssignModalOpen(true)}
              title="Asignar un KPI existente a un área específica"
            >
              <div className="action-icon">🔗</div>
              <div className="action-label">Nueva Asignación</div>
              <div className="action-description">Vincular KPI-Área</div>
            </button>

            <button
              className="action-card"
              onClick={() => setMetaModalOpen(true)}
              title="Establecer objetivos mensuales para un KPI asignado"
            >
              <div className="action-icon">🎯</div>
              <div className="action-label">Nueva Meta</div>
              <div className="action-description">Definir objetivo</div>
            </button>

            <button
              className="action-card highlight"
              onClick={() => setValModalOpen(true)}
              title="Registrar valores de KPIs manualmente por día"
            >
              <div className="action-icon">✏️</div>
              <div className="action-label">Agregar Valor</div>
              <div className="action-description">Entrada manual</div>
            </button>
          </div>
        </div>

        {/* Sección de importación masiva */}
        <div className="import-section">
          <div className="import-card">
            <div className="import-header">
              <h3 className="import-title">
                <span style={{marginRight: 8}}>📁</span>
                Importación Masiva de Datos
              </h3>
              <div 
                className="help-badge"
                onClick={() => {
                  Modal.info({
                    title: 'Formato del Excel para Importación',
                    content: (
                      <div style={{marginTop: 16}}>
                        <p style={{marginBottom: 12}}>El archivo Excel debe contener las siguientes columnas:</p>
                        <table style={{width: '100%', borderCollapse: 'collapse'}}>
                          <thead>
                            <tr style={{borderBottom: '2px solid #003087'}}>
                              <th style={{textAlign: 'left', padding: 8, color: '#003087'}}>Columna</th>
                              <th style={{textAlign: 'left', padding: 8, color: '#003087'}}>Descripción</th>
                              <th style={{textAlign: 'left', padding: 8, color: '#003087'}}>Ejemplo</th>
                            </tr>
                          </thead>
                          <tbody>
                            <tr style={{borderBottom: '1px solid #e8f2ff'}}>
                              <td style={{padding: 8}}><strong>KPI_Codigo</strong></td>
                              <td style={{padding: 8}}>Código del indicador</td>
                              <td style={{padding: 8, fontFamily: 'monospace'}}>ACUERDOS_Q</td>
                            </tr>
                            <tr style={{borderBottom: '1px solid #e8f2ff'}}>
                              <td style={{padding: 8}}><strong>Area</strong></td>
                              <td style={{padding: 8}}>Nombre del área</td>
                              <td style={{padding: 8, fontFamily: 'monospace'}}>ADAMANTINE</td>
                            </tr>
                            <tr style={{borderBottom: '1px solid #e8f2ff'}}>
                              <td style={{padding: 8}}><strong>FechaMedicion</strong></td>
                              <td style={{padding: 8}}>Fecha del valor</td>
                              <td style={{padding: 8, fontFamily: 'monospace'}}>4/08/2025</td>
                            </tr>
                            <tr>
                              <td style={{padding: 8}}><strong>Valor</strong></td>
                              <td style={{padding: 8}}>Valor numérico</td>
                              <td style={{padding: 8, fontFamily: 'monospace'}}>400</td>
                            </tr>
                          </tbody>
                        </table>
                        <div style={{marginTop: 16, padding: 12, background: '#e7f0ff', borderRadius: 8}}>
                          <p style={{margin: 0, fontSize: 13}}>
                            <strong>Nota:</strong> Puedes subir múltiples filas con diferentes KPIs y fechas. 
                            El sistema procesará automáticamente todos los registros válidos.
                          </p>
                        </div>
                      </div>
                    ),
                    okText: 'Entendido',
                    width: 600,
                  });
                }}
                title="Ver formato requerido del archivo Excel"
              >
                <span className="help-icon">?</span>
                <span>Ayuda formato</span>
              </div>
            </div>
            
            <div className="import-content">
              <Upload {...uploadProps}>
                <div className="upload-area">
                  <div className="upload-icon">📊</div>
                  <div className="upload-text">
                    <p className="upload-main">Arrastra tu archivo Excel aquí</p>
                    <p className="upload-sub">o haz clic para seleccionar</p>
                  </div>
                  <div className="upload-formats">
                    Formatos: .xlsx, .xls, .csv
                  </div>
                </div>
              </Upload>
              
              {selectedFile && (
                <div className="file-selected">
                  <span className="file-icon">📄</span>
                  <span className="file-name">{selectedFile.name}</span>
                  <span className="file-status">Listo para preview</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tablas de datos con estilo mejorado */}
        <div className="data-sections">
          {/* Definiciones */}
          <div className="data-section">
            <div className="section-header-admin">
              <h3 className="section-title">
                <span className="section-icon">📋</span>
                Definiciones de KPIs
              </h3>
              <div className="section-badge">{kpiDefs.length} registros</div>
            </div>
            <div className="table-wrapper">
              <Table
                dataSource={kpiDefs}
                columns={defsColumns}
                rowKey={(r) => r.KPIID}
                pagination={{ 
                  pageSize: 8,
                  showSizeChanger: false,
                  showTotal: (total, range) => `${range[0]}-${range[1]} de ${total}` 
                }}
                className="admin-table"
              />
            </div>
          </div>

          {/* Asignaciones */}
          <div className="data-section">
            <div className="section-header-admin">
              <h3 className="section-title">
                <span className="section-icon">🔗</span>
                Asignaciones KPI-Área
              </h3>
              <div className="section-badge">{asignaciones.length} registros</div>
            </div>
            <div className="table-wrapper">
              <Table
                dataSource={asignaciones}
                columns={asignColumns}
                rowKey={(r) => r.KPIAsignacionID}
                pagination={{ 
                  pageSize: 8,
                  showSizeChanger: false,
                  showTotal: (total, range) => `${range[0]}-${range[1]} de ${total}` 
                }}
                className="admin-table"
              />
            </div>
          </div>

          {/* Metas */}
          <div className="data-section">
            <div className="section-header-admin">
              <h3 className="section-title">
                <span className="section-icon">🎯</span>
                Metas Mensuales
              </h3>
              <div className="section-badge">{metas.length} registros</div>
            </div>
            <div className="table-wrapper">
              <Table
                dataSource={metas}
                columns={metasColumns}
                rowKey={(r) => r.MetaAsignID ?? Math.random()}
                pagination={{ 
                  pageSize: 8,
                  showSizeChanger: false,
                  showTotal: (total, range) => `${range[0]}-${range[1]} de ${total}` 
                }}
                className="admin-table"
              />
            </div>
          </div>
        </div>
        {/* Def Modal */}
        <Modal
          title={editingDef ? "Editar KPI" : "Nuevo KPI"}
          open={defModalOpen}
          onOk={onDefModalOk}
          onCancel={onDefModalCancel}
        >
          <Form form={formDef} layout="vertical">
            <Form.Item
              name="Codigo"
              label="Código"
              rules={[{ required: true }]}
            >
              <Input />
            </Form.Item>
            <Form.Item
              name="Nombre"
              label="Nombre"
              rules={[{ required: true }]}
            >
              <Input />
            </Form.Item>
            <Form.Item name="Descripcion" label="Descripción">
              <Input.TextArea rows={2} />
            </Form.Item>
            <Form.Item name="Unidad" label="Unidad">
              <Input />
            </Form.Item>
            <Form.Item name="Perspectiva" label="Perspectiva">
              <Input />
            </Form.Item>
            <Form.Item name="Peso" label="Peso">
              <InputNumber
                min={0}
                max={10}
                step={0.1}
                style={{ width: "100%" }}
              />
            </Form.Item>
            <Form.Item name="Activo" label="Activo" initialValue={1}>
              <Select>
                <Option value={1}>Sí</Option>
                <Option value={0}>No</Option>
              </Select>
            </Form.Item>
          </Form>
        </Modal>

        {/* Assign Modal */}
        <Modal
          title="Crear Asignación"
          open={assignModalOpen}
          onOk={onAssignModalOk}
          onCancel={onAssignModalCancel}
        >
          <Form form={formAssign} layout="vertical">
            <Form.Item name="KPIID" label="KPI" rules={[{ required: true }]}>
              <Select showSearch optionFilterProp="children">
                {kpiDefs.map((k) => (
                  <Option key={k.KPIID} value={k.KPIID}>
                    {k.Codigo} — {k.Nombre}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="AreaID"
              label="Area (selecciona)"
              rules={[{ required: true }]}
            >
              <Select showSearch optionFilterProp="children">
                {areas.map((a) => (
                  <Option
                    key={a.idArea ?? a.id}
                    value={a.idArea ?? a.id ?? a.areaId}
                  >
                    {(a.idArea ?? a.id ?? a.areaId) +
                      " - " +
                      (a.nombreArea ?? a.nombre ?? a.descripcion ?? a.name)}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            
          </Form>
        </Modal>

        {/* Meta Modal */}
        <Modal
          title="Crear Meta"
          open={metaModalOpen}
          onOk={onMetaModalOk}
          onCancel={onMetaModalCancel}
        >
          <Form form={formMeta} layout="vertical">
            <Form.Item
              name="KPI_Codigo"
              label="KPI (Código)"
              rules={[{ required: true }]}
            >
              <Select showSearch optionFilterProp="children">
                {kpiDefs.map((k) => (
                  <Option key={k.Codigo} value={k.Codigo}>
                    {k.Codigo} — {k.Nombre}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="AreaID"
              label="Area (selecciona)"
              rules={[{ required: true }]}
            >
              <Select showSearch optionFilterProp="children">
                {areas.map((a) => (
                  <Option
                    key={a.idArea ?? a.id}
                    value={a.idArea ?? a.id ?? a.areaId}
                  >
                    {(a.idArea ?? a.id ?? a.areaId) +
                      " - " +
                      (a.nombreArea ?? a.nombre ?? a.descripcion ?? a.name)}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="Periodo"
              label="Periodo (mes)"
              rules={[{ required: true }]}
            >
              <DatePicker picker="month" style={{ width: "100%" }} />
            </Form.Item>
            <Form.Item
              name="ValorMeta"
              label="Valor Meta"
              rules={[{ required: true }]}
            >
              <InputNumber
                style={{ width: "100%" }}
                step={0.01}
                formatter={(v) =>
                  v == null || v === "" ? "" : Number(v).toLocaleString()
                }
                parser={(v) => v?.replace(/[^\d\.\-]/g, "")}
              />
            </Form.Item>
          </Form>
        </Modal>

        {/* Manual value modal (lista de KPI) */}
        <Modal
          title="Agregar valor manual (varios KPI)"
          open={valModalOpen}
          onOk={onValModalOk}
          onCancel={() => {
            formVal.resetFields();
            setValModalOpen(false);
          }}
          width={900}
          centered
        >
          <Form
            form={formVal}
            layout="vertical"
            initialValues={{
              rows: [{ KPI_Codigo: undefined, Valor: undefined }],
              targetAreas: [],
            }}
          >
            <div style={{ display: "flex", gap: 12, marginBottom: 8 }}>
              <Form.Item
                name="targetAreas"
                label={
                  <span>
                    Área(s){" "}
                    <small style={{ color: "#888" }}>
                      {" "}
                      (selecciona 1 o varias)
                    </small>
                  </span>
                }
                rules={[
                  { required: true, message: "Selecciona al menos 1 área" },
                ]}
                style={{ flex: 1 }}
              >
                <Select
                  mode="multiple"
                  showSearch
                  placeholder="Selecciona áreas..."
                  optionFilterProp="children"
                  allowClear
                >
                  {areas.map((a) => (
                    <Option
                      key={a.idArea ?? a.id ?? a.areaId}
                      value={a.idArea ?? a.id ?? a.areaId}
                    >
                      {(a.idArea ?? a.id ?? a.areaId) +
                        " - " +
                        (a.nombreArea ?? a.nombre ?? a.descripcion ?? a.name)}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                name="Fecha"
                label="Fecha"
                rules={[{ required: true, message: "Selecciona fecha" }]}
              >
                <DatePicker />
              </Form.Item>
            </div>

            <div style={{ marginBottom: 6 }}>
              <small>
                Añade las filas de KPI que quieras insertar (por cada área
                seleccionada se insertará cada fila). La tabla es scrollable si
                la lista es larga.
              </small>
            </div>

            <Form.List name="rows">
              {(fields, { add, remove }) => (
                <>
                  <div
                    style={{
                      border: "1px solid #ddd",
                      borderRadius: 4,
                      maxHeight: 320,
                      overflow: "auto",
                      padding: 8,
                      marginBottom: 12,
                      background: "#fff",
                    }}
                  >
                    <table
                      style={{ width: "100%", borderCollapse: "collapse" }}
                    >
                      <thead>
                        <tr>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "6px 8px",
                              borderBottom: "1px solid #eee",
                            }}
                          >
                            KPI
                          </th>
                          <th
                            style={{
                              textAlign: "left",
                              padding: "6px 8px",
                              borderBottom: "1px solid #eee",
                              width: 160,
                            }}
                          >
                            Valor
                          </th>
                          <th
                            style={{
                              width: 40,
                              borderBottom: "1px solid #eee",
                            }}
                          ></th>
                        </tr>
                      </thead>
                      <tbody>
                        {fields.map((field, idx) => (
                          <tr key={field.key}>
                            <td
                              style={{
                                padding: 8,
                                borderBottom: "1px solid #f4f4f4",
                              }}
                            >
                              <Form.Item
                                {...field}
                                name={[field.name, "KPI_Codigo"]}
                                fieldKey={[field.fieldKey, "KPI_Codigo"]}
                                rules={[
                                  { required: true, message: "Selecciona KPI" },
                                ]}
                                style={{ margin: 0 }}
                              >
                                <Select
                                  showSearch
                                  optionFilterProp="children"
                                  placeholder="Selecciona KPI..."
                                  style={{ minWidth: 260 }}
                                >
                                  {kpiDefs.map((k) => (
                                    <Option key={k.Codigo} value={k.Codigo}>
                                      {k.Codigo} — {k.Nombre}
                                    </Option>
                                  ))}
                                </Select>
                              </Form.Item>
                            </td>

                            <td
                              style={{
                                padding: 8,
                                borderBottom: "1px solid #f4f4f4",
                              }}
                            >
                              <Form.Item
                                {...field}
                                name={[field.name, "Valor"]}
                                fieldKey={[field.fieldKey, "Valor"]}
                                rules={[
                                  { required: true, message: "Ingresa valor" },
                                ]}
                                style={{ margin: 0 }}
                              >
                                <InputNumber style={{ width: "100%" }} />
                              </Form.Item>
                            </td>

                            <td
                              style={{
                                padding: 8,
                                borderBottom: "1px solid #f4f4f4",
                                textAlign: "center",
                              }}
                            >
                              <Button
                                type="text"
                                danger
                                onClick={() => remove(field.name)}
                                size="small"
                              >
                                ✕
                              </Button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>

                  <div style={{ display: "flex", gap: 8 }}>
                    <Button onClick={() => add()} type="dashed">
                      + Agregar fila
                    </Button>
                    <Button
                      onClick={() =>
                        formVal.setFieldsValue({
                          rows: [{ KPI_Codigo: undefined, Valor: undefined }],
                        })
                      }
                    >
                      Reset filas
                    </Button>
                  </div>
                </>
              )}
            </Form.List>
          </Form>
        </Modal>

        <Modal
          title="Subir Excel — seleccionar áreas"
          open={uploadModalOpen}
          onOk={async () => {
            if (!uploadCandidateFile) {
              message.error("No hay archivo seleccionado");
              return;
            }
            await uploadExcelToBackend(
              uploadCandidateFile,
              selectedUploadAreas
            );
            setUploadCandidateFile(null);
            setSelectedUploadAreas([]);
            setUploadModalOpen(false);
          }}
          onCancel={() => {
            setUploadCandidateFile(null);
            setSelectedUploadAreas([]);
            setUploadModalOpen(false);
          }}
          okText="Subir y procesar"
          cancelText="Cancelar"
        >
          <div style={{ marginBottom: 8 }}>
            <div style={{ marginBottom: 6 }}>
              Selecciona una o varias áreas a las cuales aplicar los valores (si
              no seleccionas ninguna, se usará el AreaID en cada fila del Excel
              si existe):
            </div>
            <Select
              mode="multiple"
              style={{ width: "100%" }}
              placeholder="Selecciona áreas..."
              value={selectedUploadAreas}
              onChange={(vals) => setSelectedUploadAreas(vals)}
              optionFilterProp="children"
              showSearch
            >
              {areas.map((a) => (
                <Option
                  key={a.idArea ?? a.id ?? a.areaId}
                  value={a.idArea ?? a.id ?? a.areaId}
                >
                  {(a.idArea ?? a.id ?? a.areaId) +
                    " - " +
                    (a.nombreArea ?? a.nombre ?? a.name ?? a.descripcion)}
                </Option>
              ))}
            </Select>
          </div>

          <div>
            <small>
              Nota: si seleccionas varias áreas, cada fila válida del Excel se
              replicará para cada área seleccionada. Si prefieres que el archivo
              tenga su propia columna Area, deja la selección vacía.
            </small>
          </div>
        </Modal>
      </div>
    );
  }
  return (
    <div style={{ maxWidth: 1400, margin: "0 auto", padding: 12 }}>
      <div
        style={{
          display: "flex",
          gap: 8,
          alignItems: "center",
          marginBottom: 12,
        }}
      >
        <Button
          type={mainTab === "dashboard" ? "primary" : "default"}
          onClick={() => setMainTab("dashboard")}
        >
          Dashboard
        </Button>
        <Button
          type={mainTab === "admin" ? "primary" : "default"}
          onClick={() => setMainTab("admin")}
        >
          KPI Admin
        </Button>
      </div>

      {mainTab === "dashboard" ? renderDashboardTab() : renderAdminTab()}
    </div>
  );
}
