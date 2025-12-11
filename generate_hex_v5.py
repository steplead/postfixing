import re
import binascii
import json

# JS Logic V5 (Uses data-var)
# JS Logic V5.1 (Reactive Auto-Calc)
js_logic = r"""
window.ozExecuteCalc = function(target) {
    // Handle both Button and Container triggers
    var container = target.hasAttribute('data-itb-calculator') ? target : target.closest('[data-itb-calculator]');
    if (!container) return;

    var id = container.getAttribute('data-itb-calculator');
    var func = window.OZ_FORMULAS[id];
    if (!func) return console.error('No formula for ' + id);

    var inputs = container.querySelectorAll('[data-var]');
    var values = {};
    inputs.forEach(function(inp) {
        var key = inp.getAttribute('data-var');
        var val = inp.value;
        if (inp.tagName === 'SELECT') {
            values[key] = val;
        } else {
            values[key] = parseFloat(val) || 0;
        }
    });

    try {
        var result = func(values);
        var outContainer = container.querySelector('.itb-outputs');
        if (!outContainer) return;

        // Mapping Mode
        for (var key in result) {
            var el = outContainer.querySelector('[data-itb-output="' + key + '"]');
            if (el) {
                var val = result[key];
                var fmt = el.getAttribute('data-itb-format');
                
                if (fmt === 'currency') {
                    if (!isNaN(parseFloat(val))) val = '$' + parseFloat(val).toFixed(2);
                } else if (fmt === 'percent') {
                    if (!isNaN(parseFloat(val))) val = parseFloat(val).toFixed(1) + '%';
                }

                el.innerText = val;
            }
        }
        outContainer.style.display = 'block';
    } catch(e) {
        console.error(e);
    }
};
window.OZ_FORMULAS = window.OZ_FORMULAS || {};
Object.assign(window.OZ_FORMULAS, {
    // Phase 10: Active Make-Up Consumption
    "makeup-consumption-calculator-active-1": function(v) {
        var d_um = parseFloat(v.d_um);
        var deltaP_bar = parseFloat(v.deltaP_bar);
        var rho = parseFloat(v.rho);
        var Cd = parseFloat(v.Cd);
        var duty = parseFloat(v.duty);

        // Logic: A = pi * (d * 1e-6)^2 / 4
        // Q = Cd * A * sqrt(2 * (P * 1e5) / rho)
        // ml/h = Q * duty/100 * 3600 * 1e6
        
        var A = Math.PI * Math.pow(d_um * 1e-6, 2) / 4;
        var Q_inst = Cd * A * Math.sqrt(2 * (deltaP_bar * 1e5) / rho);
        var Q_active = Q_inst * (duty / 100);
        var q_ml_h = Q_active * 3600 * 1e6;
        var q_inst_mlh = Q_inst * 3600 * 1e6; // Theoretical max if duty 100%

        return {
            q_ml_h: q_ml_h.toFixed(1),
            q_active_mlh: q_ml_h.toFixed(1),
            q_inst_mlh: q_inst_mlh.toFixed(1), // Optional debug output
            note: "Calculated via Orifice Eq."
        };
    },

    // 1. Bottling Line Capacity Calculator
    "capacity-calculator-2026": function(v) {
        var dailyProductionTarget = parseFloat(v.dailyProductionTarget);
        var operatingHoursPerDay = parseFloat(v.operatingHoursPerDay);
        var operatingDaysPerYear = parseFloat(v.operatingDaysPerYear);
        var plannedDowntimePercentage = parseFloat(v.plannedDowntimePercentage);

        var effectiveOperatingHours = operatingHoursPerDay * (1 - plannedDowntimePercentage / 100);
        var requiredBPH = Math.ceil(dailyProductionTarget / effectiveOperatingHours);
        var annualCapacity = dailyProductionTarget * operatingDaysPerYear;
        var recommendedBPH = Math.ceil(requiredBPH * 1.15);
        var utilizationRate = (requiredBPH / recommendedBPH) * 100;

        return {
            requiredBPH: requiredBPH,
            recommendedBPH: recommendedBPH,
            annualCapacity: annualCapacity,
            utilizationRate: utilizationRate.toFixed(1)
        };
    },

    // 2. TCO Calculator (TIJ vs Laser)
    "tco-calculator-2026": function(v) {
        var dailyProduction = parseFloat(v.dailyProduction);
        var daysPerYear = parseFloat(v.daysPerYear);
        var tijCost = parseFloat(v.tijCost);
        var printsPerCart = parseFloat(v.printsPerCart);
        var laserCapex = parseFloat(v.laserCapex);
        var yearsAmort = parseFloat(v.yearsAmort);

        var annualVolume = dailyProduction * daysPerYear;
        var tijAnnualCost = (annualVolume / printsPerCart) * tijCost;
        var laserAnnualAmort = laserCapex / yearsAmort;
        var laserOpEx = 500; // Fixed OpEx assumption
        var laserTotalAnnual = laserAnnualAmort + laserOpEx;
        // var tijCostPerPrint = tijCost / printsPerCart; // Not displayed
        var savings = Math.abs(tijAnnualCost - laserTotalAnnual);

        return {
            annualVolume: annualVolume,
            tijAnnualCost: tijAnnualCost.toFixed(2),
            laserTotalAnnual: laserTotalAnnual.toFixed(2),
            savings: savings.toFixed(2)
        };
    },

    // 3. Energy Cost Calculator
    "energy-cost-calculator-2026": function(v) {
        var lineSpeed = parseFloat(v.lineSpeed); // BPH
        var energyConsumptionOld = parseFloat(v.energyConsumptionOld); // kWh/1k
        var energyConsumptionNew = parseFloat(v.energyConsumptionNew); // kWh/1k
        var electricityCost = parseFloat(v.electricityCost);
        var operatingHours = parseFloat(v.operatingHours);

        var annualBottlesOld = lineSpeed * operatingHours;
        var annualEnergyOld = (annualBottlesOld / 1000) * energyConsumptionOld;
        var annualEnergyNew = (annualBottlesOld / 1000) * energyConsumptionNew;
        var annualEnergySavings = annualEnergyOld - annualEnergyNew;
        var annualCostSavings = annualEnergySavings * electricityCost;
        var savingsPercentage = ((annualEnergyOld - annualEnergyNew) / annualEnergyOld) * 100;

        return {
            annualEnergySavings: Math.round(annualEnergySavings),
            annualCostSavings: annualCostSavings.toFixed(2),
            savingsPercentage: savingsPercentage.toFixed(1)
        };
    },

    // 4. Incoterms Cost Calculator
    "incoterms-cost-calculator-2026": function(v) {
        var fobPrice = parseFloat(v.fobPrice);
        var freightCost = parseFloat(v.freightCost);
        var insuranceRate = parseFloat(v.insuranceRate);
        var customsDutyRate = parseFloat(v.customsDutyRate);
        var customsBrokerFee = parseFloat(v.customsBrokerFee);

        var cifBeforeInsurance = fobPrice + freightCost;
        var insuranceCost = cifBeforeInsurance * (insuranceRate / 100);
        var cifPrice = cifBeforeInsurance + insuranceCost;
        var customsDuty = cifPrice * (customsDutyRate / 100);
        var totalLandedCost = cifPrice + customsDuty + customsBrokerFee;
        var additionalCostPercentage = ((totalLandedCost - fobPrice) / fobPrice) * 100;

        return {
            cifPrice: cifPrice.toFixed(2),
            customsDuty: customsDuty.toFixed(2),
            totalLandedCost: totalLandedCost.toFixed(2),
            additionalCostPercentage: additionalCostPercentage.toFixed(1)
        };
    },

    // 5. ROI Payback Calculator
    "roi-payback-calculator-2026": function(v) {
        var equipmentInvestment = parseFloat(v.equipmentInvestment);
        var annualSavings = parseFloat(v.annualSavings);
        var operatingYears = parseFloat(v.operatingYears);
        var taxRate = parseFloat(v.taxRate);
        var maintenanceCost = parseFloat(v.maintenanceCost);

        var netAnnualSavings = annualSavings - maintenanceCost;
        var afterTaxAnnualProfit = netAnnualSavings * (1 - taxRate / 100);
        var totalAfterTaxProfit = afterTaxAnnualProfit * operatingYears;
        
        var roi = ((totalAfterTaxProfit - equipmentInvestment) / equipmentInvestment) * 100;
        var paybackPeriod = equipmentInvestment / afterTaxAnnualProfit;
        var annualROI = (afterTaxAnnualProfit / equipmentInvestment) * 100;

        return {
            afterTaxAnnualProfit: afterTaxAnnualProfit.toFixed(2),
            paybackPeriod: paybackPeriod.toFixed(1),
            roi: roi.toFixed(1),
            annualROI: annualROI.toFixed(1)
        };
    },

    // --- PHASE 2: LEGACY TOOLS ---

    // 6. PG Estimator
    "pg-estimator-class3": function(v) {
        var fp = parseFloat(v.fp);
        var ibp = parseFloat(v.ibp);
        var pg = "Review";
        var comment = "Check regulations";

        if (fp < 23 && ibp <= 35) {
            pg = "I";
            comment = "Top Hazard (Boiling < 35°C)";
        } else if (fp < 23 && ibp > 35) {
            pg = "II";
            comment = "Standard Flammable (FP < 23°C)";
        } else if (fp >= 23 && fp <= 60) {
            pg = "III";
            comment = "Low Flammability (FP 23-60°C)";
        }

        return { pg: pg, comment: comment };
    },

    // 7. SDS Version Compare
    "sds-version-compare": function(v) {
        return {
            note: "Audit: SDS Rev " + v.rev + " confirmed. FP=" + v.fp + "C, IBP=" + v.ibp + "C."
        };
    },

    // 8. UN 4G Decoder
    "un-4g-code-decoder": function(v) {
        // e.g., 4G/Y25/S/25/USA/+ID
        var parts = v.code.split('/');
        if (parts.length < 5) return { explain: "Invalid Code Format" };
        
        var type = parts[0]; // 4G
        var perf = parts[1]; // Y25
        var pg = perf.charAt(0) === 'X' ? 'I/II/III' : (perf.charAt(0) === 'Y' ? 'II/III' : 'III');
        var gross = perf.substring(1);
        var solid = parts[2] === 'S' ? 'Solids/Inner-Packagings' : 'Liquids (Pressure Tested)';
        
        return {
            explain: "Type: " + type + ", PG: " + pg + ", Max Gross: " + gross + "kg, Content: " + solid
        };
    },

    // 9. LQ Eligibility Checker
    "lq-eligibility-checker": function(v) {
        var m = v.mode;
        var p = v.pg;
        var ml = parseFloat(v.inner_ml);
        var ok = "No";
        var mark = "None";

        if (m.indexOf('Ground') !== -1) {
            if ((p === 'I' && ml <= 500) || (p === 'II' && ml <= 1000) || (p === 'III' && ml <= 5000)) {
                ok = "Yes"; mark = "LQ Diamond";
            }
        } else if (m === 'Air') {
            if (p !== 'I' && ml <= 1000) { // Rough heuristic
                ok = "Maybe (Y-LQ)"; mark = "Y-LQ Diamond";
            }
        } else if (m === 'Sea') {
            if (ml <= 1000 && (p === 'II' || p === 'III')) {
                ok = "Yes (Check IMDG)"; mark = "LQ Diamond";
            }
        }
        return { ok: ok, mark: mark };
    },

    // 10. LQ Matrix Builder
    "lq-matrix-builder-01": function(v) {
        var ml = parseFloat(v.inner_ml);
        var qty = parseFloat(v.qty);
        var rho = parseFloat(v.rho);
        var tare = parseFloat(v.tare);
        
        var net_l = (ml * qty) / 1000;
        var gross = (net_l * rho) + tare;
        
        // Re-use logic from checker roughly
        var elig = "See Checker";
        if (gross > 30) elig = "Exceeds 30kg Cap!";
        else elig = "Likely OK (Check specifics)";

        return {
            net_l: net_l.toFixed(2),
            gross: gross.toFixed(1),
            elig: elig
        };
    },

    // 11. Outer Count
    "outer-count-calculator": function(v) {
        var t = parseFloat(v.total_l);
        var i = parseFloat(v.inner_l);
        var p = parseFloat(v.per_outer);
        var outers = Math.ceil((t / i) / p);
        return { outers: outers };
    },

    // 12. Carrier Acceptance Note
    "carrier-acceptance-note": function(v) {
        return {
            line: v.carrier + " (" + v.route + "): " + v.unpsn + " => " + v.status + ". Contact: " + v.contact
        };
    },

    // 13. Audit Sheet
    "audit-sheet-builder": function(v) {
        return {
            summary: "Audit: SDS=" + v.sds + ", Class=" + v.class + ", PG=" + v.pg + ", LQ=" + v.lq + ", Docs=" + v.docs
        };
    },

    // 14. Label Size
    "label-size-checker": function(v) {
        var mm = parseFloat(v.face_mm);
        var dist = parseFloat(v.distance_m);
        var edge = "100x100 mm";
        var note = "Standard";
        
        if (mm > 400 || dist > 3) {
            edge = "150x150 mm"; // Recommendation
            note = "Large package/distance";
        }
        return { edge: edge, note: note };
    },

    // --- PHASE 3: CIJ TOOLS ---

    // 15. CIJ Breakpoint
    "cij-print-quality-checklist-breakpoint-explainer-01": function(v) {
        var visc = parseFloat(v.visc);
        var mod = parseFloat(v.mod);
        var risk = "Low";
        var tip = "Optimal param window";
        
        if (visc < 3.5 || visc > 5.5) {
            risk = "High (Viscosity)";
            tip = "Correct viscosity first";
        } else if (mod < 20 || mod > 80) {
            risk = "Medium (Modulation)";
            tip = "Adjust modulation voltage";
        }
        return { risk: risk, tip: tip };
    },

    // 16. CIJ Adhesion
    "cij-print-quality-checklist-adhesion-checker-02": function(v) {
        var sub = v.substrate;
        var surf = v.surface;
        var fam = v.inkfam;
        
        var risk = "Low";
        var action = "Proceed";
        
        if (surf !== 'Dry') {
            risk = "High (Surface State)";
            action = "Clean/Dry or use Acetone";
        } else if (sub === 'PE' || sub === 'OPP film') {
            risk = "Medium (Low Surface Energy)";
            action = "Check Dyne level / Flame treat";
        } else if (sub === 'Glass' && surf === 'Condensation') {
            risk = "Critical";
            action = "Air knifes required";
        }
        
        return { risk: risk, action: action };
    },

    // --- PHASE 4: INK SHELF LIFE TOOLS (17) ---

    // 1. Storage Temp Risk
    "cij-ink-shelf-life-storage-temp-risk-1": function(v) {
        var avg = parseFloat(v.avg_t);
        var min = parseFloat(v.oem_min);
        var max = parseFloat(v.oem_max);
        var type = v.ink_type;
        
        var diff = 0;
        if (avg < min) diff = min - avg;
        if (avg > max) diff = avg - max;
        
        var risk = "OK";
        if (diff > 0) risk = "CAUTION";
        if (diff > 3) risk = "HIGH";
        
        if (type === "UV-curable" && risk === "CAUTION") risk = "HIGH";
        
        return { risk: risk };
    },

    // 2. FIFO & Acc
    "cij-ink-shelf-life-storage-fifo-2": function(v) {
        var mfg = v.mfg_date; // YYYY-MM
        var w = parseFloat(v.warranty_mo);
        // Simple string handling for date
        var parts = mfg.split("-");
        var y = parseInt(parts[0]);
        var m = parseInt(parts[1]);
        
        m += w;
        while(m > 12) { m -= 12; y++; }
        
        var use_by = y + "-" + (m < 10 ? "0"+m : m);
        
        // Warmup parsing "20 / 30" maybe? Or formatted string
        // Actually logic says "If ΔT ≥ 10...". Input is string? No, let's assume user enters "10 / 25" style or just checks delta.
        // Wait, definition said input type string "Move from / to". 
        // Let's rely on simple heuristic or just fixed text if complex.
        // "Explain: Allow several hours if ΔT is big"
        // Let's return the explanation directly.
        
        return { use_by: use_by, warmup_tip: "Plan ≥3h if ΔT ≥ 10°C" };
    },

    // 3. RH Impact
    "cij-ink-shelf-life-storage-rh-impact-3": function(v) {
        var rh = parseFloat(v.rh);
        var fam = v.ink_family;
        
        var dry = 1.0;
        var decap = 1.0;
        
        if (fam.indexOf("TIJ") > -1) {
            // Linear approx 35->0.8, 75->1.4
            dry = 0.8 + (rh - 35) * (0.6 / 40);
            if (rh < 40) decap = 2.0; // Sensitive
        }
        
        return { dry_factor: dry.toFixed(2) + "x", decap_factor: decap.toFixed(2) + "x" };
    },

    // 4. UV Risk
    "cij-ink-shelf-life-storage-uv-risk-4": function(v) {
        var lux = parseFloat(v.lux);
        var t = parseFloat(v.exposure_min);
        var pkg = v.packaging;
        
        var score = (lux * t) / 1000;
        if (pkg.indexOf("Opaque") > -1) score *= 0.4;
        if (pkg.indexOf("Black") > -1) score *= 0.6;
        if (pkg.indexOf("Clear") > -1) score *= 1.2;
        
        var final = Math.min(100, Math.ceil(score));
        return { uv_score: final + "/100" };
    },

    // 5. Orientation
    "cij-ink-shelf-life-storage-orientation-5": function(v) {
        var cart = v.cartridge;
        var white = v.pigment;
        var tip = "Upright (Septum Up)";
        if (white.indexOf("White") > -1) tip += " + Weekly Roll";
        return { tip: tip };
    },

    // 6. Agitation
    "cij-ink-shelf-life-storage-agitation-6": function(v) {
        var b = parseFloat(v.bottles);
        var d = parseFloat(v.days);
        var perDay = Math.ceil(b / d);
        return { schedule: perDay + " bottles/day", signoff: d + " slots" };
    },

    // 7. Hygiene
    "cij-ink-shelf-life-storage-hygiene-7": function(v) {
        return { tasks: "1. Clean Cap | 2. Lint-free Wipe | 3. No Sticks | 4. Waste Bin | 5. Gloves" };
    },

    // 8. AQL
    "cij-ink-shelf-life-storage-aql-8": function(v) {
        var lot = parseFloat(v.lot);
        // Simple lookup simulation
        var n = 10;
        var c = 0;
        if (lot > 1000) n = 80;
        else if (lot > 100) n = 20;
        
        // AQL logic simplified
        var aql = parseFloat(v.aql);
        c = Math.floor(n * aql / 100); 
        
        return { n: n, c: c + " defects" };
    },

    // 9. Viscosity Drift
    "cij-ink-shelf-life-storage-viscosity-9": function(v) {
        var base = parseFloat(v.base_visc);
        var loss = parseFloat(v.solvent_loss);
        var dt = Math.abs(parseFloat(v.delta_t));
        
        var vNew = base * (1 + (loss/100)*2) + (dt * 0.1);
        return { visc: vNew.toFixed(2) };
    },

    // 10. Evap
    "cij-ink-shelf-life-storage-evap-10": function(v) {
        var h = parseFloat(v.run_hours);
        var l = parseFloat(v.makeup_l);
        var t = parseFloat(v.avg_t);
        
        var rate = l / h;
        if (t > 25) rate *= 1.2;
        
        return { evap_index: rate.toFixed(4) + " L/h" };
    },

    // 11. Fireload
    "cij-ink-shelf-life-storage-fireload-11": function(v) {
        var meq = parseFloat(v.meq_l);
        var cap = parseFloat(v.cabinet_cap);
        var rcap = parseFloat(v.room_cap);
        
        var s = "OK";
        if (meq > cap) s = "Exceeds Cabinet!";
        if (meq > rcap) s = "Exceeds Room!";
        
        return { status: s };
    },

    // 12. Decap
    "cij-ink-shelf-life-storage-decap-12": function(v) {
        var fam = v.ink_family;
        var rh = parseFloat(v.rh);
        var base = 30; // min
        
        if (fam.indexOf("aqueous") > -1) base = 15;
        if (rh < 40) base *= 0.5;
        
        return { idle_window: Math.floor(base) + " min" };
    },

    // 13. Q10 Shelf Life
    "cij-ink-shelf-life-storage-q10-13": function(v) {
        var sl = parseFloat(v.shelf_months);
        var tr = parseFloat(v.t_ref);
        var ta = parseFloat(v.t_actual);
        var q = parseFloat(v.q10);
        
        var dt = (ta - tr) / 10;
        var factor = Math.pow(q, dt);
        var adj = sl / factor;
        
        return { adj_months: adj.toFixed(1) + " mo" };
    },

    // 14. Logistics
    "cij-ink-shelf-life-storage-logistics-14": function(v) {
        var r = v.region;
        var c = "Insulated";
        var w = "3h";
        if (r.indexOf("Tropical") > -1) { c="Reefer"; w="6h"; }
        return { controls: c, warmup: w };
    },

    // 15. ROI
    "cij-ink-shelf-life-storage-roi-15": function(v) {
        var clogs = parseFloat(v.clogs);
        var labor = parseFloat(v.labor);
        var scrap = parseFloat(v.ink_scrap);
        // Cost assumptions: 1 clog = 1h labor?
        var cost = (clogs * labor) + (scrap * 100); // 100/L assumed
        return { savings: "$" + cost.toFixed(0) };
    },
    
    // 16. FIFO Monitor
    "cij-ink-shelf-life-storage-fifomonitor-16": function(v) {
        // v.lots string "202301, 202305, 202212"
        var flag = "Pass";
        // logic placeholder
        if (v.lots.indexOf("2024") > -1 && v.lots.indexOf("2023") > -1) flag = "Check Sort";
        return { flag: flag };
    },
    
    // 17. Calendar
    "cij-ink-shelf-life-storage-calendar-17": function(v) {
        return { checklist: "Jan: Freeze | Jul: Heat | Oct: RH High" };
    },

    // --- PHASE 5: NOZZLE CLOGGING TOOLS (8) ---

    // 1. Make-Up Planner
    "itb-makeup-planner-v4": function(v) {
        var t = parseFloat(v.tempC);
        var h = parseFloat(v.hours);
        var n = v.nozzle;
        var d = parseFloat(v.duty);
        var p = parseFloat(v.price || 18);
        
        // Base consumption factor k (ml/h) estimation
        var k = 6;
        if (n === "60") k = 8;
        if (n === "75") k = 10;
        
        // Temp factor: +5% per deg > 20
        var tFactor = 1 + 0.05 * (t - 20);
        // Duty factor: 0.5 static + 0.5 * duty (evaporation vs usage)
        var dFactor = 0.5 + 0.5 * (d / 100);
        
        var ml = k * h * tFactor * dFactor;
        var cost = (ml / 1000) * p;
        
        return { mu_est: ml.toFixed(0) + " ml", budget: "$" + cost.toFixed(2) };
    },

    // 2. Humidity Static
    "itb-humidity-static-v5": function(v) {
        var rh = parseFloat(v.rh);
        var sub = v.substrate;
        var spd = parseFloat(v.speed);
        
        var risk = "Low";
        var count = "Grounding";
        
        var score = 0;
        if (rh < 40) score += 2;
        if (sub.indexOf("film") > -1 || sub.indexOf("PET") > -1) score += 2;
        if (spd > 150) score += 1;
        
        if (score >= 4) {
            risk = "High";
            count = "Active Ionizers + Humidification";
        } else if (score >= 2) {
            risk = "Medium";
            count = "Passive Brushes + Check RH";
        }
        
        return { risk: risk, primary: count };
    },

    // 3. ESD Energy
    "itb-esd-energy-v3": function(v) {
        var c_pf = parseFloat(v.cap);
        var v_kv = parseFloat(v.volt);
        
        // E = 0.5 * C * V^2
        // pF -> F: * 1e-12
        // kV -> V: * 1e3
        var c_f = c_pf * 1e-12;
        var vol_v = v_kv * 1000;
        
        var j = 0.5 * c_f * Math.pow(vol_v, 2);
        var mj = j * 1000;
        
        return { energy: mj.toFixed(2) + " mJ" };
    },

    // 4. Startup Timer
    "itb-startup-timer-v2": function(v) {
        var tech = v.tech;
        var s = parseFloat(v.seconds);
        var limit = (tech === "TIJ") ? 30 : 180;
        
        var status = (s <= limit) ? "Pass" : "FAIL (Late)";
        return { flag: status };
    },

    // 5. Shutdown Compliance
    "itb-shutdown-compliance-v3": function(v) {
        var tot = parseFloat(v.stops);
        var cln = parseFloat(v.cleanstops);
        
        if (tot === 0) return { pct: "0%", flag: "-" };
        
        var p = (cln / tot) * 100;
        var f = "Good";
        if (p < 98) f = "Warning";
        if (p < 95) f = "Risk";
        
        return { pct: p.toFixed(1) + "%", flag: f };
    },

    // 6. Filter Life
    "itb-filter-life-v3": function(v) {
        var b = parseFloat(v.base);
        var n = parseFloat(v.now);
        var h = parseFloat(v.hours);
        
        // Load %
        var load = 0;
        if (n > b) load = (n - b) / (100 - b) * 100;
        
        var adv = "OK";
        if (load > 70 || h > 2000) adv = "Plan Change";
        if (load > 90 || h > 3000) adv = "CHANGE NOW";
        
        return { load: load.toFixed(0) + "%", advice: adv };
    },

    // 7. KPI Mini
    "itb-kpi-mini-v3": function(v) {
        var stops = parseFloat(v.stops);
        var clean = parseFloat(v.clean);
        var t = parseFloat(v.tests);
        var p = parseFloat(v.pass);
        var mu = parseFloat(v.mu);
        var mub = parseFloat(v.mu_base);
        
        var cs = (stops > 0) ? (clean/stops)*100 : 0;
        var fp = (t > 0) ? (p/t)*100 : 0;
        var dr = (mub > 0) ? ((mu - mub)/mub)*100 : 0;
        
        return {
            cs: cs.toFixed(1) + "%",
            fp: fp.toFixed(1) + "%",
            drift: (dr > 0 ? "+" : "") + dr.toFixed(1) + "%"
        };
    },

    // 8. SEO Density
    "itb-seo-density-v1": function(v) {
        var tot = parseFloat(v.total_words);
        var occ = parseFloat(v.occurs);
        
        var d = (occ / tot) * 100;
        var s = "Low";
        if (d >= 0.5 && d <= 2.5) s = "Good (~1%)";
        if (d > 2.5) s = "High (Stuffing?)";
        
        return { density: d.toFixed(2) + "%", status: s };
    },

    // --- PHASE 6: Compatible vs OEM Fluids ---
    // 1. TCO
    "cij-compatible-vs-oem-tco-1": function(v) {
        var ib = parseFloat(v.ink_burn) || 0;
        var mb = parseFloat(v.makeup_burn) || 0;
        var hr = parseFloat(v.line_hours) || 0;
        
        var l_ink = ib * hr / 1000.0;
        var l_mu = mb * hr / 1000.0;
        
        var events = parseFloat(v.events) || 0;
        var chg_time = parseFloat(v.chg_time) || 0;
        var dt_cost = parseFloat(v.dt_cost) || 0;
        var cost_chg = events * chg_time * dt_cost;
        
        var fail_oem = 12 * (parseFloat(v.fail_prob_oem)||0) * 0.01 * (parseFloat(v.fail_impact)||0);
        var fail_comp = 12 * (parseFloat(v.fail_prob_comp)||0) * 0.01 * (parseFloat(v.fail_impact)||0);
        
        var cost_oem = (l_ink * (parseFloat(v.ink_price_oem)||0)) + (l_mu * (parseFloat(v.makeup_price_oem)||0)) + cost_chg + fail_oem;
        var cost_comp = (l_ink * (parseFloat(v.ink_price_comp)||0)) + (l_mu * (parseFloat(v.makeup_price_comp)||0)) + cost_chg + fail_comp;
        
        return {
            tco_oem: cost_oem.toFixed(0),
            tco_comp: cost_comp.toFixed(0),
            delta: (cost_oem - cost_comp).toFixed(0)
        };
    },

    // 2. Stability Logger
    "cij-jet-stability-logger": function(v) {
        var voltage = Math.abs(parseFloat(v.voltage)||0);
        var mu_rate = parseFloat(v.mu_rate) || 0;
        var cleans = parseFloat(v.cleans) || 0;
        var restart = parseFloat(v.restart) || 0;
        
        var flag = "Green";
        var note = "Stable operation";
        
        if (voltage >= 5 || mu_rate >= 100 || cleans > 6 || restart < 98) {
            flag = "Amber";
            note = "Monitor closely; verify filtration";
        }
        if (voltage >= 10 || mu_rate >= 150 || cleans > 10 || restart < 90) {
            flag = "Red";
            note = "Out of spec: Stop & Fix";
        }
        
        return { flag: flag, note: note };
    },

    // ==========================================
    // PHASE 7: SOLVENT SAFETY & MSDS TOOLS (9 Items)
    // ==========================================

    // 1. SDS Completeness Validator (Transport Focus)
    "sds-completeness-validator-transport-focus": function(inputs) {
        var un = (inputs.un || "").trim();
        var psn = (inputs.psn || "").trim();
        var cls = (inputs.class || "").trim();
        var pg = inputs.pg || "";
        var air = inputs.air || "No";
        var score = 0;
        var gaps = [];
        var advice = "Ready to review.";

        if(un) score += 20; else gaps.push("UN Number");
        if(psn) score += 20; else gaps.push("PSN");
        if(cls) score += 20; else gaps.push("Class");
        if(pg) score += 20; else gaps.push("Packing Group");
        if(inputs.rev) score += 20; else gaps.push("Revision Date");

        if(air === "Yes" && (!un || un.toLowerCase() === "na" || un.toLowerCase() === "not regulated")) {
            advice = "CRITICAL: Air shipment requires UN number. 'Not Regulated' is rarely valid for CIJ solvents by air.";
        } else if(score === 100) {
            advice = "SDS appears structurally complete for transport.";
        } else {
            advice = "Fill missing fields before booking freight.";
        }

        return {
            score: score + "%",
            gaps: gaps.length ? gaps.join(", ") : "None",
            advice: advice
        };
    },

    // 2. Mixture Flash Point Estimator (Educational)
    "mixture-flash-point-estimator-educational": function(inputs) {
        var fp1 = parseFloat(inputs.fp1) || 0;
        var w1 = parseFloat(inputs.w1) || 0;
        var fp2 = parseFloat(inputs.fp2) || 0;
        var w2 = parseFloat(inputs.w2) || 0;
        
        // Very rough "lowest flash point dominates" heuristic
        var est = Math.min(fp1, fp2);
        
        // If the lower FP component is < 10% mass, maybe it rises? 
        // For safety/training, we stick to "flash point is determined by the most volatile component".
        
        return {
            fp_mix: "~" + est.toFixed(1) + " \u00b0C (Estimate)",
            caveat: "This is a Training Value. Actual FP must be tested (ASTM D93)."
        };
    },

    // 3. PG & PI Assistant (Training Aid)
    "pg-pi-assistant-training-aid": function(inputs) {
        var fp = parseFloat(inputs.fp) || 0;
        var ibp = parseFloat(inputs.ibp) || 0;
        var air = inputs.air || "No";
        
        var pg = "Unknown";
        if(ibp <= 35) {
            pg = "I (High Danger)";
        } else if(fp < 23) {
            pg = "II (Medium Danger)";
        } else if(fp >= 23 && fp <= 60) {
            pg = "III (Low Danger)";
        } else if(fp > 60) {
            pg = "Non-DG (unless heated)";
        }
        
        var hint = "-";
        if(air === "Yes") {
            if(pg.includes("I")) hint = "Forbidden on Pax? Check PI 3XX.";
            if(pg.includes("II")) hint = "Likely PI 353 (Pax) / 364 (Cargo).";
            if(pg.includes("III")) hint = "Likely PI 355 (Pax) / 366 (Cargo).";
        }
        
        return {
            pg_guess: pg,
            air_hint: hint,
            next: "Verify against specific UN entry in IATA DGR."
        };
    },

    // 4. DDP LQ Eligibility Checker
    "ddp-lq-eligibility-checker-air-sea-road": function(inputs) {
        var mode = inputs.mode || "Air (IATA)";
        var inner = parseFloat(inputs.inner_vol) || 0;
        var gross = parseFloat(inputs.gross) || 0;
        var pg = inputs.pg || "II";
        
        var eligible = "Likely NO";
        var req = "Full DG Class 3 Labels + Papers";
        var doc = "Shipper's Declaration (DGD)";
        
        if(mode.includes("Air")) {
            // Air LQ usually limit 1L (PG II) or 10L (PG III) per inner? 
            // Broad rule: PG II often 1L inner / 30kg package (Y PI).
            var maxInner = (pg === "II") ? 1000 : ((pg === "III") ? 5000 : 0); // mL
            if(inner <= maxInner && gross <= 30) {
                eligible = "Yes (Y-Pack)";
                req = "'Y' LQ Mark + Class 3 Label + UN ID";
                doc = "DGD Required (Nature & Qty: 'LTD QTY')";
            } else {
                eligible = "No (Too large/PG I)";
            }
        } else if (mode.includes("Sea") || mode.includes("Road")) {
            // IMDG/ADR often 5L inner / 30kg gross for Class 3 PG II/III
            var maxInnerSea = 5000; 
            if(inner <= maxInnerSea && gross <= 30) {
                eligible = "Yes";
                req = "LQ Mark (Diamond)";
                doc = (mode.includes("Sea")) ? "DG Manifest" : "Checking exemptions...";
            }
        }
        
        return {
            elig: eligible,
            req: req,
            doc: doc,
            notes: "Must use combination packaging."
        };
    },

    // 5. UN Box Mark Decoder
    "un-box-mark-decoder": function(inputs) {
        var mark = (inputs.mark || "").trim();
        // format: UN 4G/Y30/S/25/USA/M4460
        // clean up
        mark = mark.replace(/^un\s+/i, "");
        var parts = mark.split("/");
        
        var type = parts[0] || "?";
        var perf = parts[1] || "?";
        var solid = parts[2] || "?";
        var year = parts[3] || "?";
        
        var pgLevel = "?";
        if(perf.toUpperCase().startsWith("X")) pgLevel = "X (PG I, II, III)";
        else if(perf.toUpperCase().startsWith("Y")) pgLevel = "Y (PG II, III)";
        else if(perf.toUpperCase().startsWith("Z")) pgLevel = "Z (PG III only)";
        
        return {
            type: type + " (e.g. Fiberboard Box)",
            pg: pgLevel,
            limit: perf.replace(/[xyz]/i, "") + " kg (Gross Mass)",
            notes: "Solids/Inner Pack flag: " + solid
        };
    },

    // 6. Closure Instruction Recorder
    "closure-instruction-recorder": function(inputs) {
        var box = inputs.box || "";
        var tape = inputs.tape || "";
        var torque = inputs.torque || "";
        
        return {
            summary: "Box: " + box + " | Tape: " + tape + " | Torque: " + torque + " Nm. Photo evidence required."
        };
    },

    // 7. Label Planner (Overpack Aware)
    "label-planner-overpack-aware": function(inputs) {
        var mode = inputs.mode || "Air";
        var lq = inputs.lq || "No";
        var ovp = inputs.overpack || "No";
        
        var reqs = [];
        if(mode === "Air") {
            if(lq.includes("Yes")) reqs.push("Y-LQ Mark");
            reqs.push("Class 3 Label");
            reqs.push("UN Number + PSN");
            reqs.push("Shipper/Consignee Addr");
            reqs.push("Orientation Arrows");
        } else {
            if(lq.includes("Yes")) reqs.push("LQ Mark (Plain)");
            else {
                reqs.push("Class 3 Label");
                reqs.push("UN Number");
            }
        }
        
        var place = "Vertical face, not crossing edge.";
        if(ovp === "Yes") {
            place += " MUST duplicate all labels on Overpack outer + 'OVERPACK' text.";
        }
        
        return {
            required: reqs.join(" + "),
            placement: place,
            print: "Check size (100x100mm)"
        };
    },

    // 8. DGD Field Validator
    "dgd-field-validator": function(inputs) {
        var un = inputs.un || "";
        var pg = inputs.pg || "";
        var inner = parseFloat(inputs.inner) || 0;
        
        var issues = [];
        if(!un.toUpperCase().startsWith("UN")) issues.push("UN# format");
        if(inner > 5000) issues.push("Inner vol high (>5L)");
        
        return {
            errors: issues.length ? issues.join(", ") : "None obvious",
            fix: issues.length ? "Review against IATA PI" : "Proceed to sign",
            notes: "Retain copy for 2 years"
        };
    },

    // 9. DDP Costing Estimator (DG-aware)
    "ddp-costing-estimator-dg-aware": function(inputs) {
        var f = parseFloat(inputs.freight) || 0;
        var dg = parseFloat(inputs.dgfee) || 0;
        var pack = parseFloat(inputs.pack) || 0;
        var cust = parseFloat(inputs.customs) || 0;
        var risk = parseFloat(inputs.risk) || 0;
        
        var sub = f + dg + pack + cust;
        var buffer = sub * (risk / 100);
        var total = sub + buffer;
        
        return {
            ddp: "$" + total.toFixed(2),
            buffer: "$" + buffer.toFixed(2),
            notes: "Includes " + risk + "% contingency."
        };
    },

    // 3. Risk Checker
    "cij-compatible-vs-oem-risk-2": function(v) {
        var crit = v.criticality || "";
        var fw = v.fw_policy || "";
        var env = v.env || "";
        var qa = v.supplier || "";
        
        var score = 1; // Tier 1 (Pilot)
        if (crit === "Zero-fail" || crit === "High") score += 1;
        if (fw === "Auto") score += 1;
        if (env === "Cold/condensation" || env === "Oily") score += 1;
        if (qa === "Unknown" || qa === "Partial (COA only)") score += 1;
        
        var tier = "Tier " + Math.min(score, 4);
        var note = "Pilot allowed";
        if (score >= 4) note = "Keep OEM";
        else if (score === 3) note = "Freeze FW, then Pilot";
        
        return { tier: tier, note: note };
    },

    // 4. Barcode Grade
    "barcode-grade-quickcheck": function(v) {
        var q = v.quiet || "Yes";
        if (q === "No") return { grade: "1.0", risk: "High (Quiet Zone violation)" };
        
        var c = parseFloat(v.contrast) || 0;
        var m = parseFloat(v.mod) || 0;
        
        // Heuristic: Grade approx (Contrast/25 + Module)/2 clamped 0..4
        // Contrast is %, e.g., 80. 80/25 = 3.2.
        var g = ((c / 25.0) + m) / 2.0;
        if (g > 4) g = 4;
        if (g < 0) g = 0;
        
        var risk = "Low";
        if (g < 2.5) risk = "Medium";
        if (g < 1.5) risk = "High";
        
        return { grade: g.toFixed(1), risk: risk };
    },

    // 5. SDS Logger
    "sds-excursion-logger": function(v) {
        var temp = parseFloat(v.temp)||0;
        var dur = parseFloat(v.hours)||0;
        var band = v.band || "A";
        
        // Parse band limits
        var maxT = 25;
        if (band.indexOf("B") !== -1) maxT = 35;
        if (band.indexOf("C") !== -1) maxT = 45;
        
        var diff = temp - maxT;
        var action = "OK to use";
        var note = "Within specs";
        
        if (diff > 5 && dur > 24) {
            action = "Sample QA";
            note = "Excursion >5C for >24h";
        } else if (diff > 0) {
            action = "Inspect seals";
            note = "Minor excursion";
        }
        
        return { action: action, note: note };
    },

    // 6. Pilot Gate
    "pilot-gate-calculator": function(v) {
        var up = parseFloat(v.uptime) || 0;
        var cl = parseFloat(v.cleans) || 0; // Delta vs OEM
        var gr = parseFloat(v.grade) || 0; // Delta grade
        var mu = parseFloat(v.mu) || 0; // Make-up delta %
        var fw = parseFloat(v.fw) || 0;
        
        var decision = "Scale";
        var reason = "All gates passed";
        
        if (up < 99.5) { decision = "Revert"; reason = "Uptime < 99.5%"; }
        else if (cl > 0) { decision = "Extend"; reason = "Head-cleans increased"; }
        else if (Math.abs(gr) > 0.3) { decision = "Revert"; reason = "Grade drift > 0.3"; }
        else if (Math.abs(mu) > 5) { decision = "Extend"; reason = "Make-up burn unstable"; }
        else if (fw > 0) { decision = "Revert/Freeze"; reason = "Firmware faults detected"; }
        
        return { decision: decision, reason: reason };
    },

    // 7. Mix Planner
    "mix-planner": function(v) {
        var lo = parseFloat(v.lines_oem)||0;
        var lc = parseFloat(v.lines_comp)||0;
        var lh = parseFloat(v.lines_hybrid)||0;
        
        var burn = parseFloat(v.avg_burn)||0;
        var hours = parseFloat(v.hours)||0;
        var po = parseFloat(v.price_oem)||0;
        var pc = parseFloat(v.price_comp)||0;
        
        var ro = parseFloat(v.risk_oem)||1;
        var rc = parseFloat(v.risk_comp)||2;
        var rh = parseFloat(v.risk_hybrid)||2;
        
        var l_per_line = burn * hours / 1000.0;
        var oem_cost = lo * l_per_line * po;
        var comp_cost = (lc + lh) * l_per_line * pc;
        
        var budget = oem_cost + comp_cost;
        
        var total_lines = lo + lc + lh;
        var score = total_lines > 0 ? ((lo*ro + lc*rc + lh*rh)/total_lines) : 0;
        
        return { budget: budget.toFixed(0), score: score.toFixed(1) };
    },

    // 8. KPI Dashboard
    "kpi-dashboard-sketch": function(v) {
        var volt = v.volt;
        var mu = v.mu;
        var cleans = v.cleans;
        var grade = v.grade;
        
        var summary = "ALERT POLICY:\\n" +
            "Voltage Drift > " + volt + "% → ALARM\\n" +
            "MU Rate > " + mu + " ml/h → WARNING\\n" +
            "Cleans > " + cleans + "/100h → REVIEW\\n" +
            "Grade < " + grade + " → STOP";
            
        return { summary: summary };
    },

    // ==========================================
    // PHASE 8: WHITE & UV INK TOOLS (2 Items)
    // ==========================================

    // 1. White Opacity & Coverage Estimator
    "cij-white-uv-ink-use-cases-opacity-1": function(inputs) {
        var sub = inputs.substrate || "Black PET";
        var dynes = parseFloat(inputs.pretreat) || 30;
        var film = parseFloat(inputs.film) || 5;
        var pigment = inputs.pigment || "TiO2 standard";
        var speed = parseFloat(inputs.speed) || 100;
        
        // Base requirement based on substrate contrast challenge
        var req = 1.0;
        if(sub.includes("Black") || sub.includes("Amber")) req = 2.0;
        if(sub.includes("Kraft")) req = 1.5; // Absorbent
        
        // Pigment bonus
        var pEff = 1.0;
        if(pigment.includes("hollow")) pEff = 1.3; // Better scattering
        
        // Film impact (thick is good)
        var fEff = film / 5.0; // Norm to 5um
        
        // Speed penalty (ink spread/thinning)
        var sPen = 1.0;
        if(speed > 600) sPen = 0.8;
        
        // Total "Coverage Power" = (Film * Pigment * SpeedPenalty)
        var power = fEff * pEff * sPen;
        
        // Passes needed = Requirement / Power
        var passes = Math.ceil(req / power);
        if(passes < 1) passes = 1;
        if(passes > 5) passes = 5; // Cap
        
        var note = "Standard setup.";
        if(dynes < 38) note = "Risk: Low surface energy (<38). Adhesion check mandatory.";
        else if(passes > 3) note = "High opacity need. Consider UV-curable or slower line.";
        else if(sub.includes("Kraft") && film < 8) note = "Porous substrate may absorb fluid; increase thickness.";
        
        return {
            passes: passes + " \u00d7",
            note: note
        };
    },

    // 2. UV Readability Checker
    "cij-white-uv-ink-use-cases-uvcheck-2": function(inputs) {
        var lamp = inputs.lamp || "365";
        var ink = inputs.ink || "Invisible";
        var sub = inputs.substrate || "Dark";
        var cam = inputs.camera || "None";
        
        var score = 5; // Start mid
        
        // Lamp match (365 is usually ideal for rare-earth/organic invisible)
        if(lamp === "365") score += 2;
        if(lamp === "395" && ink.includes("Invisible")) score -= 1; // Bleed into visible violet
        
        // Contrast
        if(sub === "Dark") {
            // Dark absorbs UV? Or reflects? usually dark eats fluorescence unless opaque
            // Actually, UV on dark is usually GOOD contrast if the ink glows bright green/red/blue.
            score += 1; 
        } else if(sub === "Light" && ink.includes("Invisible")) {
            // Invisible on white paper uses OBAs? Conflict.
            score -= 2; 
        }
        
        // Camera
        if(cam.includes("Narrow")) score += 3; // Cuts ambient
        if(cam === "None") score -= 1; // Human eye only is tricky for high speed
        
        // Cap
        if(score > 10) score = 10;
        if(score < 1) score = 1;
        
        var tip = "Check filter B/W.";
        if(score < 5) tip = "Poor signal. Try 365nm lamp + Band-pass filter.";
        else if(sub === "Light") tip = "Watch for Optical Brighteners (OBAs) in paper background.";
        else tip = "Good robust signal expected.";
        
        return {
            rating: score + "/10",
            tip: tip
        };
    },

    // =========================================
    // PHASE 9: WET ADHESION TOOLS (7 Items)
    // =========================================

    // 1. OWRK Explainer
    "cij-adhesion-wet-pet-glass-owrk-1": function(inputs) {
        var sub = inputs.substrate || "PET (untreated)";
        var gamma = parseFloat(inputs.gamma_l) || 40;
        var theta = parseFloat(inputs.theta) || 35;
        
        // WA = gamma * (1 + cos(theta)) roughly
        var thetaRad = theta * Math.PI / 180;
        var wa = gamma * (1 + Math.cos(thetaRad));
        
        var tip = "Good";
        if(wa < 45) tip = "Risk: Low adhesion";
        if(sub.includes("untreated") && theta > 60) tip = "Activate first!";
        if(sub.includes("Glass") && theta < 15) tip = "Excellent wetting";
        
        return {
            wa: wa.toFixed(1),
            tip: tip
        };
    },

    // 2. Dyne Window Calculator
    "cij-adhesion-dyne-window-3": function(inputs) {
        var dyne = parseFloat(inputs.pet_dyne) || 54;
        var margin = parseFloat(inputs.margin) || 8;
        
        var high = dyne - margin;
        var low = dyne - (margin + 4); 
        
        if (low < 20) low = 20;

        return {
            low: low.toFixed(1),
            high: high.toFixed(1),
            note: (high < 30) ? "Very difficult ink target" : "Standard generic/MEK range"
        };
    },

    // 3. Venting/Silane Checker
    "cij-adhesion-wet-pet-glass-venting-2": function(inputs) {
        var sub = inputs.substrate || "Glass (clean)";
        var ink = parseFloat(inputs.ink_tension) || 42;
        var silane = inputs.silane || "No";
        
        var subDyne = 250; // Glass default
        if(sub.includes("untreated")) subDyne = 44;
        if(sub.includes("corona")) subDyne = 54;
        
        var diff = subDyne - ink;
        var result = "Pass";
        var advice = "Proceed";
        
        if (diff < 8) {
            result = "Fail (Wetting)";
            advice = "Boost dyne or lower ink tension";
        }
        
        if (sub.includes("Glass")) {
            if (silane === "No") {
                result = "Risky (Long Term)";
                advice = "Add silane for humidity resistance";
            } else if (silane.includes("unknown")) {
                result = "Verify Process";
                advice = "Check pH & dwell";
            }
        }
        
        return {
            result: result,
            advice: advice
        };
    },

    // 4. Air Knife Estimator
    "cij-adhesion-airknife-4": function(inputs) {
        var dist = parseFloat(inputs.distance) || 180;
        var speed = parseFloat(inputs.speed) || 36;
        var film = parseFloat(inputs.initfilm) || 60;
        
        // vreq approx 5 + 0.2*film + 0.05*speed + 0.02*dist
        var vreq = 5 + (0.2 * film) + (0.05 * speed) + (0.02 * dist);
        if (vreq > 120) vreq = 120; // Cap
        
        return {
            vreq: vreq.toFixed(1) + " m/s",
            note: (vreq > 80) ? "High velocity needed (compressor?)" : "Blower sufficient"
        };
    },

    // 5. Theta Target Planner
    "cij-adhesion-theta-target-5": function(inputs) {
        var sub = inputs.substrate || "PET (treated)";
        var duty = inputs.duty || "Dry ambient";
        
        var base = (sub.includes("PET")) ? 35 : 15;
        
        if (duty.includes("Condensation")) base -= (sub.includes("PET") ? 5 : 3);
        if (duty.includes("Rinse") || duty.includes("Cold")) base -= (sub.includes("PET") ? 8 : 5);
        
        if (base < 5) base = 5; // Min physical limit usually
        
        return {
            theta_target: "< " + base + "\u00b0",
            ops: (base < 15) ? "Aggressive activation/priming required" : "Standard treatment OK"
        };
    },

    // 6. DOE Builder
    "cij-adhesion-doe-6": function(inputs) {
        var factors = inputs.factors || [];
        // factors is array if multi-select, assuming here standard single select for MVP or comma string?
        // Wait, multiple select handling in v13? 
        // My inputs parsing logic: if SELECT multiple? No, standard select returns value. 
        // If the user meant "count of factors", the input allows "Factors" selection. 
        // Let's assume input is just one factor selected to Add, but the tool implied "Builder".
        // Actually the HTML input is just a single Select. Let's act as if it estimates runs for a standard set.
        
        // Simplified Logic: Just 1 factor selected? No, let's pretend inputs.factors is a string.
        var k = 3; // Default 3 factors for standard DOE
        if (factors.includes("PET")) k++;
        if (factors.includes("Ink")) k++;
        
        var rep = parseFloat(inputs.rep) || 3;
        
        // Fake it for the single select limitation:
        // If they select "PET Dyne", we assume they are testing that + 2 others.
        // Actually, let's just make it simple.
        var runs = Math.pow(2, 3) * rep; // 2^3 * rep
        
        return {
            runs: runs,
            tip: "Full Factorial (2-level, 3 factors)"
        };
    },

    // 7. Ops Readiness Check
    "cij-adhesion-ops-check-7": function(inputs) {
        var pet = parseFloat(inputs.pet_dyne) || 52;
        var ink = parseFloat(inputs.ink) || 44;
        var primer = inputs.primer || "N/A";
        var air = parseFloat(inputs.air) || 80;
        
        var score = 100;
        var actions = [];
        
        // PET logic
        var margin = pet - ink;
        if (margin < 8) {
            var pen = (8 - margin) * 5;
            score -= pen;
            actions.push("Raise PET dyne");
        }
        
        // Primer logic
        if (primer.includes("late") || primer === "N/A") {
             // mild penalty if N/A implies not needed? assuming context
             if (primer.includes("late")) {
                 score -= 20;
                 actions.push("Fix primer timing");
             }
        }
        
        // Air logic
        if (air < 60) {
            score -= 10;
            actions.push("Boost air velocity");
        }
        
        if (score < 0) score = 0;
        
        return {
            score: score + "/100",
            action: (actions.length > 0) ? actions[0] : "Ready to print"
        };
    },

    // --- PHASE 10: MAKE-UP CONSUMPTION TOOLS (1 Item) ---
    // 1. Active Make-Up Consumption
    "makeup-consumption-calculator-active-1": function(inputs) {
        var d_um = parseFloat(inputs.d_um) || 60;
        var p_bar = parseFloat(inputs.deltaP_bar) || 2.0;
        var rho = parseFloat(inputs.rho) || 789;
        var cd = parseFloat(inputs.Cd) || 0.97;
        var duty = parseFloat(inputs.duty) || 15;

        // Physics
        var d_m = d_um * 1e-6;
        var radius_m = d_m / 2.0;
        var area_m2 = Math.PI * Math.pow(radius_m, 2);
        
        var p_pa = p_bar * 1e5;
        
        // Q = Cd * A * sqrt(2 * dP / rho)
        var q_inst_m3s = cd * area_m2 * Math.sqrt((2 * p_pa) / rho);
        
        // Active Q
        var q_active_m3s = q_inst_m3s * (duty / 100.0);
        
        // Convert to mL/h: m3/s * 3600 s/h * 1e6 ml/m3
        var q_inst_mlh = q_inst_m3s * 3600 * 1e6;
        var q_active_mlh = q_active_m3s * 3600 * 1e6;

        return {
            q_inst_mlh: q_inst_mlh.toFixed(1) + " ml/h",
            q_active_mlh: q_active_mlh.toFixed(1) + " ml/h",
            note: "Active consumption @" + duty + "% duty cycle"
        };
    }

});

// --- v13 Engine (Reactive) ---
// Listen for Input Changes (Auto-Calc)
// Listen for Input Changes (Text/Number)
document.addEventListener('input', function(e) {
    var container = e.target.closest('[data-itb-calculator]');
    if (container) {
        window.ozExecuteCalc(container);
    }
});

// Listen for Change Events (Select/Radio/Checkbox) - CRITICAL FIX
document.addEventListener('change', function(e) {
    var container = e.target.closest('[data-itb-calculator]');
    if (container) {
        window.ozExecuteCalc(container);
    }
});

// Initial boot
var calcs = document.querySelectorAll('[data-itb-calculator]');
calcs.forEach(function(c) { window.ozExecuteCalc(c); });

console.log('OZ: v5.1 Reactive Engine Fully Loaded');
"""

# Check for Smart Quotes
if "’" in js_logic or "“" in js_logic or "”" in js_logic:
    print("FATAL ERROR: Smart quotes detected in JS logic!")
    exit()

# Hex Encode
hex_payload = binascii.hexlify(js_logic.encode('utf-8')).decode('utf-8')

# Final Verification
print(f"Payload Length: {len(hex_payload)}")
print(f"Sample: {hex_payload[:50]}...")

# Injection Logic
# Level 5 Loader: Timeout Decoupled
loader_script_v13_reactive = """<script>!function(){if(!window.ozExecuteCalc)window.ozExecuteCalc=function(){console.warn("OZ: Loading...")};function l(){setTimeout(function(){var e=document.getElementById("oz-safe-code");if(e){var v=e.value;if(v&&v.length%2===0){var s="";for(var i=0;i<v.length;i+=2)s+=String.fromCharCode(parseInt(v.substr(i,2),16));window.eval(s)}}}, 500)}if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",l);else l();}();</script>"""

loader_html = f"""<!-- OZ Calc v13.0 Reactive (Auto-Calc) -->
<div class="oz-calculator-app" style="font-size:0;line-height:0;margin:0;padding:0;display:inline;">
<input type="hidden" id="oz-safe-code" value="{hex_payload}">
{loader_script_v13_reactive}
<style>.oz-calculator-app {{ margin:0; padding:0; font-size:0; line-height:0; }}.itb-outputs {{ display: block; margin-top: 20px; padding: 15px; background: #f0fdf4; border: 1px solid #16a34a; border-radius: 6px; font-size: 16px; line-height: 1.5; }}.itb-output-group {{ margin-bottom: 8px; display: flex; justify-content: space-between; border-bottom: 1px dashed #bbf7d0; padding-bottom: 4px; }}.itb-output-group:last-child {{ border-bottom: none; }}</style>
</div>"""

loader_html = re.sub(r'\n', '', loader_html)

# Read original
with open('errorpost.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Strip existing loader blocks (Aggressive)
# We look for the marker, or just the bottom section
if '<!-- OZ Calc' in content:
    content = content.split('<!-- OZ Calc')[0]

# Strip existing loader blocks (Aggressive)
# We look for the marker, or just the bottom section
if '<!-- OZ Calc' in content:
    content = content.split('<!-- OZ Calc')[0]

# Hide Buttons (Don't delete, just hide)
# This appeases WP auto-formatters that might try to "fix" a missing button
# content = re.sub(r'<button', r'<button style="display:none !important;"', content)

# Strip any trailing newlines
content = content.rstrip()

# Inject
final_content = content + "\n" + loader_html

with open('errorpost.html', 'w', encoding='utf-8') as f:
    f.write(final_content)

print("INJECTION COMPLETE: Updated errorpost.html with v5 Payload (data-var support).")
