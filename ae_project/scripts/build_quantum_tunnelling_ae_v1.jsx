(function () {
    var FPS = 60;
    var W = 1920;
    var H = 1080;
    var ROOT = "C:/Users/liuzh/Desktop/1";
    var OUT_AEP = ROOT + "/ae_project/quantum_tunnelling_AE_rebuild_v1.aep";

    var C = {
        bg: [0.0, 0.0, 0.0],
        nearBlack: [0.0196, 0.0275, 0.0431],
        white: [1.0, 1.0, 1.0],
        gray: [0.533, 0.533, 0.533],
        blue: [0.345, 0.769, 0.867],
        cyan: [0.361, 0.816, 0.702],
        red: [0.988, 0.384, 0.333],
        yellow: [1.0, 1.0, 0.0],
        purple: [0.604, 0.447, 0.675],
        green: [0.514, 0.757, 0.404],
        orange: [1.0, 0.525, 0.184],
        deepOrange: [0.75, 0.12, 0.025]
    };

    var FONT_CN = "NotoSansSC-Regular";
    var FONT_CN_BOLD = "NotoSansSC-Bold";
    var FONT_MATH = "CambriaMath";

    function tf(layer, matchName) {
        return layer.property("ADBE Transform Group").property(matchName);
    }

    function applyEase(prop, influence) {
        var i;
        var inf = influence || 72;
        try {
            for (i = 1; i <= prop.numKeys; i++) {
                prop.setInterpolationTypeAtKey(i, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
                prop.setTemporalAutoBezierAtKey(i, true);
                prop.setTemporalContinuousAtKey(i, true);
            }
        } catch (e) {}
    }

    function setKeys(prop, times, values, ease) {
        var i;
        try { prop.setValuesAtTimes(times, values); }
        catch (bulkError) {
            for (i = 0; i < times.length; i++) prop.setValueAtTime(times[i], values[i]);
        }
        if (ease !== false) applyEase(prop, 72);
    }

    function setSampledKeys(prop, times, values) {
        var i;
        try { prop.setValuesAtTimes(times, values); }
        catch (bulkError) {
            for (i = 0; i < times.length; i++) prop.setValueAtTime(times[i], values[i]);
        }
        try { prop.expression = "posterizeTime(20); value;"; } catch (e) {}
    }

    function setHoldKeys(prop, times, values) {
        var i;
        for (i = 0; i < times.length; i++) {
            prop.setValueAtTime(times[i], values[i]);
        }
        for (i = 1; i <= prop.numKeys; i++) {
            prop.setInterpolationTypeAtKey(i, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);
        }
    }

    function addBackground(comp, name, color) {
        var bg = comp.layers.addSolid(color || C.bg, name || "BG", W, H, 1, comp.duration);
        bg.moveToEnd();
        return bg;
    }

    function addNull(comp, name) {
        var n = comp.layers.addNull(comp.duration);
        n.name = name;
        n.guideLayer = true;
        n.shy = true;
        tf(n, "ADBE Anchor Point").setValue([0, 0]);
        tf(n, "ADBE Position").setValue([0, 0]);
        return n;
    }

    function addText(comp, name, text, pos, size, color, align, font) {
        var l = comp.layers.addText(text);
        l.name = name;
        var p = l.property("ADBE Text Properties").property("ADBE Text Document");
        var td = p.value;
        td.fontSize = size;
        td.fillColor = color || C.white;
        td.applyFill = true;
        td.applyStroke = false;
        td.tracking = 0;
        td.leading = size * 1.25;
        try { td.font = font || FONT_CN; } catch (e) {}
        if (align === "left") td.justification = ParagraphJustification.LEFT_JUSTIFY;
        else if (align === "right") td.justification = ParagraphJustification.RIGHT_JUSTIFY;
        else td.justification = ParagraphJustification.CENTER_JUSTIFY;
        p.setValue(td);
        tf(l, "ADBE Position").setValue(pos || [W / 2, H / 2]);
        l.motionBlur = true;
        return l;
    }

    function shapeFromPoints(points, closed) {
        var s = new Shape();
        var z = [];
        var i;
        s.vertices = points;
        for (i = 0; i < points.length; i++) z.push([0, 0]);
        s.inTangents = z;
        s.outTangents = z;
        s.closed = !!closed;
        return s;
    }

    function addPath(comp, name, points, color, width, closed, fillColor, fillOpacity) {
        var l = comp.layers.addShape();
        l.name = name;
        var root = l.property("ADBE Root Vectors Group");
        var g = root.addProperty("ADBE Vector Group");
        g.name = name + "_PATH";
        var vectors = g.property("ADBE Vectors Group");
        var path = vectors.addProperty("ADBE Vector Shape - Group");
        path.property("ADBE Vector Shape").setValue(shapeFromPoints(points, closed));
        if (fillColor) {
            var fill = vectors.addProperty("ADBE Vector Graphic - Fill");
            fill.property("ADBE Vector Fill Color").setValue(fillColor);
            fill.property("ADBE Vector Fill Opacity").setValue(fillOpacity === undefined ? 100 : fillOpacity);
        }
        if (width > 0) {
            var stroke = vectors.addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(color || C.white);
            stroke.property("ADBE Vector Stroke Width").setValue(width);
            stroke.property("ADBE Vector Stroke Line Cap").setValue(2);
        }
        tf(l, "ADBE Position").setValue([0, 0]);
        l.motionBlur = true;
        var livePath = l.property("ADBE Root Vectors Group")
            .property(1)
            .property("ADBE Vectors Group")
            .property("ADBE Vector Shape - Group")
            .property("ADBE Vector Shape");
        return { layer: l, path: livePath };
    }

    function addRect(comp, name, pos, size, fillColor, fillOpacity, strokeColor, strokeWidth, roundness) {
        var l = comp.layers.addShape();
        l.name = name;
        var root = l.property("ADBE Root Vectors Group");
        var g = root.addProperty("ADBE Vector Group");
        var vectors = g.property("ADBE Vectors Group");
        var r = vectors.addProperty("ADBE Vector Shape - Rect");
        r.property("ADBE Vector Rect Size").setValue(size);
        r.property("ADBE Vector Rect Position").setValue([0, 0]);
        if (roundness) r.property("ADBE Vector Rect Roundness").setValue(roundness);
        if (fillColor) {
            var fill = vectors.addProperty("ADBE Vector Graphic - Fill");
            fill.property("ADBE Vector Fill Color").setValue(fillColor);
            fill.property("ADBE Vector Fill Opacity").setValue(fillOpacity === undefined ? 100 : fillOpacity);
        }
        if (strokeColor && strokeWidth > 0) {
            var stroke = vectors.addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(strokeColor);
            stroke.property("ADBE Vector Stroke Width").setValue(strokeWidth);
        }
        tf(l, "ADBE Position").setValue(pos);
        l.motionBlur = true;
        var liveRect = l.property("ADBE Root Vectors Group")
            .property(1)
            .property("ADBE Vectors Group")
            .property("ADBE Vector Shape - Rect");
        return { layer: l, size: liveRect.property("ADBE Vector Rect Size"), position: tf(l, "ADBE Position") };
    }

    function addCircle(comp, name, pos, diameter, fillColor, fillOpacity, strokeColor, strokeWidth) {
        var l = comp.layers.addShape();
        l.name = name;
        var root = l.property("ADBE Root Vectors Group");
        var g = root.addProperty("ADBE Vector Group");
        var vectors = g.property("ADBE Vectors Group");
        var e = vectors.addProperty("ADBE Vector Shape - Ellipse");
        e.property("ADBE Vector Ellipse Size").setValue([diameter, diameter]);
        if (fillColor) {
            var fill = vectors.addProperty("ADBE Vector Graphic - Fill");
            fill.property("ADBE Vector Fill Color").setValue(fillColor);
            fill.property("ADBE Vector Fill Opacity").setValue(fillOpacity === undefined ? 100 : fillOpacity);
        }
        if (strokeColor && strokeWidth > 0) {
            var stroke = vectors.addProperty("ADBE Vector Graphic - Stroke");
            stroke.property("ADBE Vector Stroke Color").setValue(strokeColor);
            stroke.property("ADBE Vector Stroke Width").setValue(strokeWidth);
        }
        tf(l, "ADBE Position").setValue(pos);
        l.motionBlur = true;
        return l;
    }

    function addArrow(comp, name, p1, p2, color, width) {
        var dx = p2[0] - p1[0];
        var dy = p2[1] - p1[1];
        var len = Math.sqrt(dx * dx + dy * dy);
        if (len < 1) len = 1;
        var ux = dx / len;
        var uy = dy / len;
        var px = -uy;
        var py = ux;
        var head = 18 + width * 2;
        var wing = 9 + width;
        var base = [p2[0] - ux * head, p2[1] - uy * head];
        var lineObj = addPath(comp, name, [p1, base], color, width, false, null, 0);
        var triObj = addPath(comp, name + "_HEAD", [p2, [base[0] + px * wing, base[1] + py * wing], [base[0] - px * wing, base[1] - py * wing]], color, 0, true, color, 100);
        var result = [lineObj.layer, triObj.layer];
        result.linePath = lineObj.path;
        result.headPath = triObj.path;
        result.strokeWidth = width;
        return result;
    }

    function arrowShapes(p1, p2, width) {
        var dx = p2[0] - p1[0];
        var dy = p2[1] - p1[1];
        var len = Math.sqrt(dx * dx + dy * dy);
        if (len < 1) len = 1;
        var ux = dx / len;
        var uy = dy / len;
        var px = -uy;
        var py = ux;
        var head = 18 + width * 2;
        var wing = 9 + width;
        var base = [p2[0] - ux * head, p2[1] - uy * head];
        return {
            line: shapeFromPoints([p1, base], false),
            head: shapeFromPoints([p2, [base[0] + px * wing, base[1] + py * wing], [base[0] - px * wing, base[1] - py * wing]], true)
        };
    }

    function animateArrowPaths(arrow, times, p1s, p2s) {
        var lines = [];
        var heads = [];
        var i;
        for (i = 0; i < times.length; i++) {
            var g = arrowShapes(p1s[i], p2s[i], arrow.strokeWidth || 4);
            lines.push(g.line);
            heads.push(g.head);
        }
        setPathKeys(arrow.linePath, times, lines);
        setPathKeys(arrow.headPath, times, heads);
    }

    function setLayerWindow(layer, start, end) {
        layer.inPoint = Math.max(0, start);
        layer.outPoint = Math.min(layer.containingComp.duration, end);
    }

    function windowChildrenOf(comp, parent, start, end) {
        var i;
        for (i = 1; i <= comp.numLayers; i++) {
            if (comp.layer(i).parent === parent) setLayerWindow(comp.layer(i), start, end);
        }
    }

    function setLayerTimeMap(layer, times, values, endTime) {
        layer.timeRemapEnabled = true;
        var p = layer.property("ADBE Time Remapping");
        // AE hides Time Remapping if its final remaining key is removed.  Keep
        // the first default key, replace everything else, then write our map.
        while (p.numKeys > 1) p.removeKey(p.numKeys);
        setKeys(p, times, values, true);
        layer.inPoint = 0;
        layer.outPoint = endTime;
    }

    function setTextKeys(layer, times, texts) {
        var p = layer.property("ADBE Text Properties").property("ADBE Text Document");
        var docs = [];
        var i;
        for (i = 0; i < times.length; i++) {
            var td = p.value;
            td.text = texts[i];
            docs.push(td);
        }
        try { p.setValuesAtTimes(times, docs); }
        catch (bulkError) {
            for (i = 0; i < times.length; i++) p.setValueAtTime(times[i], docs[i]);
        }
        try { p.expression = "posterizeTime(20); value;"; } catch (e) {}
    }

    function fade(layer, t0, t1, t2, t3) {
        var p = tf(layer, "ADBE Opacity");
        if (t0 !== undefined && t1 !== undefined) {
            p.setValueAtTime(t0, 0);
            p.setValueAtTime(t1, 100);
        }
        if (t2 !== undefined && t3 !== undefined) {
            p.setValueAtTime(t2, 100);
            p.setValueAtTime(t3, 0);
        }
        applyEase(p, 70);
    }

    function gaussianWave(center, y, sigma, amp, cycles, phase, x0, x1, count, squared) {
        var pts = [];
        var i;
        var n = count || 120;
        for (i = 0; i <= n; i++) {
            var x = x0 + (x1 - x0) * i / n;
            var q = (x - center) / sigma;
            var env = Math.exp(-0.5 * q * q);
            var yy;
            if (squared) yy = y - amp * env * env;
            else yy = y - amp * env * Math.sin((x - center) / cycles * Math.PI * 2 + phase);
            pts.push([x, yy]);
        }
        return shapeFromPoints(pts, false);
    }

    function setPathKeys(prop, times, shapes) {
        var i;
        for (i = 0; i < times.length; i++) prop.setValueAtTime(times[i], shapes[i]);
        applyEase(prop, 70);
    }

    function addGaussianWaveLayer(comp, name, color, width, y, times, centers, sigmas, amps, cycles, phases, squared) {
        var holder = addPath(comp, name, [[100, y], [1820, y]], color, width, false, null, 0);
        var shapes = [];
        var i;
        for (i = 0; i < times.length; i++) {
            shapes.push(gaussianWave(centers[i], y, sigmas[i], amps[i], cycles[i], phases[i], 120, 1800, 160, squared));
        }
        setPathKeys(holder.path, times, shapes);
        return holder.layer;
    }

    function addBlur(layer, amount) {
        try {
            var fx = layer.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2");
            fx.property(1).setValue(amount);
            try { fx.property(3).setValue(true); } catch (e2) {}
        } catch (e) {}
    }

    function addGuideSafeArea(comp) {
        var g = addRect(comp, "[GUIDE] SAFE AREA", [960, 540], [1728, 918], null, 0, C.gray, 1, 0).layer;
        g.guideLayer = true;
        g.shy = true;
        tf(g, "ADBE Opacity").setValue(20);
        g.enabled = false;
    }

    function makeFolder(name, parent) {
        var f = app.project.items.addFolder(name);
        if (parent) f.parentFolder = parent;
        return f;
    }

    function makeComp(name, frames, folder) {
        var c = app.project.items.addComp(name, W, H, 1, frames / FPS, FPS);
        c.bgColor = C.bg;
        c.motionBlur = true;
        c.shutterAngle = 180;
        c.shutterPhase = -90;
        if (folder) c.parentFolder = folder;
        addBackground(c, "BG_BLACK", C.bg);
        addGuideSafeArea(c);
        return c;
    }

    function importFootage(path, name, folder) {
        var f = new File(path);
        if (!f.exists) throw new Error("Missing media: " + f.fsName);
        var io = new ImportOptions(f);
        var item = app.project.importFile(io);
        item.name = name;
        if (folder) item.parentFolder = folder;
        return item;
    }

    function addReferenceMarker(comp, time, comment) {
        var mv = new MarkerValue(comment);
        comp.markerProperty.setValueAtTime(time, mv);
    }

    function buildFusion(sceneFolder) {
        var comp = makeComp("S01_FUSION_AE_49s", 2940, sceneFolder);
        // The title and Sun share one zoom curve.  Their base widths are set at
        // roughly 1:100, so the title is readable only while the Sun is still
        // far larger than the frame, exactly like a camera pulling back.
        var title = addText(comp, "TITLE_核聚变", "核聚变", [960, 430], 2.0, C.white, "center", FONT_CN_BOLD);
        setKeys(tf(title, "ADBE Scale"), [0, 7.0], [[10500, 10500], [100, 100]], true);
        setKeys(tf(title, "ADBE Position"), [0, 7.0], [[960, 430], [960, 240]], true);
        setKeys(tf(title, "ADBE Opacity"), [0, 4.6, 6.2], [100, 100, 0], true);

        var sunGlow = addCircle(comp, "SUN_GLOW", [960, 28250], 600, C.orange, 25, null, 0);
        var sunOuter = addCircle(comp, "SUN_OUTER", [960, 28250], 520, C.deepOrange, 100, C.orange, 2);
        var sunMid = addCircle(comp, "SUN_MID", [960, 28250], 410, C.orange, 100, null, 0);
        var sunCore = addCircle(comp, "SUN_CORE", [960, 28250], 260, C.yellow, 78, null, 0);
        addBlur(sunGlow, 75);
        addBlur(sunCore, 22);
        var suns = [sunGlow, sunOuter, sunMid, sunCore];
        var i;
        for (i = 0; i < suns.length; i++) {
            setKeys(tf(suns[i], "ADBE Position"), [0, 7.2], [[960, 28250], [960, 650]], true);
            setKeys(tf(suns[i], "ADBE Scale"), [0, 7.2], [[10500, 10500], [100, 100]], true);
            setKeys(tf(suns[i], "ADBE Opacity"), [13.45, 14.25], [tf(suns[i], "ADBE Opacity").value, 0], true);
        }
        setKeys(tf(sunGlow, "ADBE Opacity"), [7.2, 9.3, 11.6, 13.45, 14.25], [18, 32, 21, 25, 0], true);
        var age = addText(comp, "SUN_AGE", "46 亿年", [1260, 650], 34, C.orange, "left", FONT_CN_BOLD);
        fade(age, 7.0, 7.8, 13.4, 14.1);

        var tempGroup = addNull(comp, "TEMP_GROUP");
        setKeys(tf(tempGroup, "ADBE Opacity"), [13.65, 14.15, 29.0, 29.55], [0, 100, 100, 0], true);
        var axis = addPath(comp, "TEMP_AXIS", [[160, 650], [1760, 650]], C.gray, 3, false, null, 0);
        axis.layer.parent = tempGroup;
        var tickX;
        for (i = 0; i <= 5; i++) {
            tickX = 240 + i * 256;
            var tick = addPath(comp, "TEMP_TICK_" + i, [[tickX, 635], [tickX, 665]], C.gray, 2, false, null, 0);
            tick.layer.parent = tempGroup;
            var tvEarly = addText(comp, "TEMP_VALUE_EARLY_" + i, String(i * 0.3), [tickX, 710], 24, C.gray, "center", FONT_MATH);
            tvEarly.parent = tempGroup;
            setKeys(tf(tvEarly, "ADBE Opacity"), [14.0, 21.5167, 22.1], [100, 100, 0], true);
            var tvLate = addText(comp, "TEMP_VALUE_LATE_" + i, String(i * 2), [tickX, 710], 25, i === 5 ? C.red : C.gray, "center", FONT_MATH);
            tvLate.parent = tempGroup;
            setKeys(tf(tvLate, "ADBE Opacity"), [14.0, 21.5167, 22.1, 29.0], [0, 0, 100, 100], true);
            setKeys(tf(tvLate, "ADBE Scale"), [21.5167, 22.15, 23.2], [[122, 122], [112, 112], [100, 100]], true);
        }
        var unitEarly = addText(comp, "TEMP_UNIT_EARLY", "×10⁷ K", [1690, 710], 26, C.gray, "center", FONT_MATH);
        unitEarly.parent = tempGroup;
        setKeys(tf(unitEarly, "ADBE Opacity"), [14.0, 21.5, 21.5167, 22.2], [100, 100, 100, 0], true);
        var unitLate = addText(comp, "TEMP_UNIT_LATE", "×10⁷ K", [1690, 710], 26, C.gray, "center", FONT_MATH);
        unitLate.parent = tempGroup;
        setKeys(tf(unitLate, "ADBE Opacity"), [21.5167, 22.1, 29.0], [0, 100, 100], true);
        var blueBar = addRect(comp, "TEMP_SOLAR_1.5e7", [880, 555], [1280, 34], C.blue, 100, null, 0, 0);
        blueBar.layer.parent = tempGroup;
        setKeys(blueBar.size, [14.0, 21.5, 21.5167, 22.3, 23.8, 25.5, 29.0], [[1280, 34], [1280, 34], [1280, 34], [480, 34], [260, 34], [192, 34], [192, 34]], true);
        setKeys(blueBar.position, [14.0, 21.5, 21.5167, 22.3, 23.8, 25.5, 29.0], [[880, 555], [880, 555], [880, 555], [480, 555], [370, 555], [336, 555], [336, 555]], true);
        var blueLabel = addText(comp, "TEMP_SOLAR_LABEL", "1.5 × 10⁷ K", [260, 520], 30, C.blue, "left", FONT_MATH);
        blueLabel.parent = tempGroup;
        var redBar = addRect(comp, "TEMP_CLASSICAL_1e8", [240, 470], [1, 34], C.red, 100, null, 0, 0);
        redBar.layer.parent = tempGroup;
        setKeys(redBar.size, [17.8, 21.5, 29.0], [[1, 34], [1280, 34], [1280, 34]], true);
        setKeys(redBar.position, [17.8, 21.5, 29.0], [[240, 470], [880, 470], [880, 470]], true);
        var redLabel = addText(comp, "TEMP_CLASSICAL_LABEL", "1 × 10⁸ K", [260, 435], 30, C.red, "left", FONT_MATH);
        redLabel.parent = tempGroup;
        fade(redLabel, 18.0, 18.5, 29.0, 29.5);
        windowChildrenOf(comp, tempGroup, 13.65, 29.55);

        var fusionGroup = addNull(comp, "FUSION_CLASSICAL_GROUP");
        setKeys(tf(fusionGroup, "ADBE Opacity"), [29.25, 29.8, 43.4, 44.0], [0, 100, 100, 0], true);
        var divider = addPath(comp, "FUSION_DIVIDER", [[960, 190], [960, 910]], C.gray, 2, false, null, 0).layer;
        divider.parent = fusionGroup;
        tf(divider, "ADBE Opacity").setValue(35);
        var reaction = addText(comp, "FUSION_REACTION", "²₁H  +  ³₁H   →   ⁴₂He  +  ¹₀n", [470, 360], 58, C.white, "center", FONT_MATH);
        reaction.parent = fusionGroup;
        var formulaHint = addText(comp, "COULOMB_HINT", "V(r) ∝ 1 / r", [470, 520], 52, C.orange, "center", FONT_MATH);
        formulaHint.parent = fusionGroup;
        var d = addCircle(comp, "NUCLEUS_D", [1260, 350], 94, C.blue, 100, C.white, 2);
        var t = addCircle(comp, "NUCLEUS_T", [1600, 350], 110, C.orange, 100, C.white, 2);
        d.parent = fusionGroup;
        t.parent = fusionGroup;
        var dText = addText(comp, "D_LABEL", "²H", [1260, 365], 38, C.white, "center", FONT_MATH);
        var tText = addText(comp, "T_LABEL", "³H", [1600, 365], 38, C.white, "center", FONT_MATH);
        dText.parent = fusionGroup;
        tText.parent = fusionGroup;
        setKeys(tf(d, "ADBE Position"), [30.0, 34.0, 36.0, 37.0], [[1260, 350], [1390, 350], [1260, 350], [1430, 350]], true);
        setKeys(tf(t, "ADBE Position"), [30.0, 34.0, 36.0, 37.0], [[1600, 350], [1470, 350], [1600, 350], [1470, 350]], true);
        setKeys(tf(dText, "ADBE Position"), [30.0, 34.0, 36.0, 37.0], [[1260, 365], [1390, 365], [1260, 365], [1430, 365]], true);
        setKeys(tf(tText, "ADBE Position"), [30.0, 34.0, 36.0, 37.0], [[1600, 365], [1470, 365], [1600, 365], [1470, 365]], true);
        var curvePts = [];
        for (i = 0; i <= 90; i++) {
            var cx = 1080 + i * 7.5;
            var cy = 850 - 390 * Math.exp(-(cx - 1080) / 150);
            curvePts.push([cx, cy]);
        }
        var coulombCurve = addPath(comp, "COULOMB_BARRIER", curvePts, C.orange, 5, false, null, 0).layer;
        coulombCurve.parent = fusionGroup;
        var particle = addCircle(comp, "CLASSICAL_NUCLEUS", [1710, 840], 34, C.white, 100, C.orange, 4);
        particle.parent = fusionGroup;
        setKeys(tf(particle, "ADBE Position"), [30.0, 33.0, 35.0, 37.0, 41.5], [[1710, 840], [1260, 690], [1550, 805], [1260, 690], [1090, 760]], true);
        windowChildrenOf(comp, fusionGroup, 29.25, 44.0);
        var question = addText(comp, "QUESTION", "?", [960, 540], 260, C.white, "center", FONT_CN_BOLD);
        setHoldKeys(tf(question, "ADBE Opacity"), [0, 43.65, 45.5833, 45.6], [0, 100, 100, 0]);
        var answer = addText(comp, "TITLE_量子隧穿", "量子隧穿", [960, 560], 172, C.white, "center", FONT_CN_BOLD);
        setHoldKeys(tf(answer, "ADBE Opacity"), [0, 45.6], [0, 100]);
        setKeys(tf(answer, "ADBE Scale"), [45.6, 49.0], [[100, 100], [110, 110]], true);
        addPath(comp, "TITLE_UNDERLINE", [[630, 690], [1290, 690]], C.blue, 5, false, null, 0).layer;
        var ul = comp.layer("TITLE_UNDERLINE");
        setHoldKeys(tf(ul, "ADBE Opacity"), [0, 45.6167], [0, 100]);
        return comp;
    }

    function buildUncertainty(sceneFolder) {
        var comp = makeComp("S02_UNCERTAINTY_AE_16_417s", 985, sceneFolder);
        var formula = addText(comp, "UNCERTAINTY_FORMULA", "σx · σp  ≥  ℏ / 2", [960, 535], 56, C.white, "center", FONT_MATH);
        fade(formula, 0.0, 0.7, 15.7, 16.35);
        var topAxis = addPath(comp, "X_AXIS", [[130, 285], [1790, 285]], C.gray, 3, false, null, 0).layer;
        var bottomAxis = addPath(comp, "P_AXIS", [[130, 790], [1790, 790]], C.gray, 3, false, null, 0).layer;
        fade(topAxis, 0.0, 0.7, 15.7, 16.35);
        fade(bottomAxis, 0.0, 0.7, 15.7, 16.35);
        var xLabel = addText(comp, "X_LABEL", "位置分布  x", [1650, 230], 34, C.blue, "right", FONT_CN_BOLD);
        var pLabel = addText(comp, "P_LABEL", "动量分布  p", [1650, 735], 34, C.red, "right", FONT_CN_BOLD);
        fade(xLabel, 0.2, 0.9, 15.7, 16.35);
        fade(pLabel, 0.2, 0.9, 15.7, 16.35);
        var times = [0, 3.4, 6.8, 10.2, 13.6, 16.4167];
        var widthsX = [520, 180, 430, 220, 500, 300];
        var widthsP = [180, 520, 220, 430, 190, 340];
        var centers = [700, 870, 1060, 1230, 900, 1040];
        var amps = [85, 125, 92, 120, 84, 105];
        var cycles = [62, 44, 58, 46, 64, 52];
        var phases = [0, 1.0, 2.0, 3.0, 4.0, 5.0];
        var waveX = addGaussianWaveLayer(comp, "X_WAVE", C.blue, 5, 285, times, centers, widthsX, amps, cycles, phases, false);
        var waveP = addGaussianWaveLayer(comp, "P_WAVE", C.red, 5, 790, times, centers, widthsP, amps, cycles, phases, false);
        fade(waveX, 0.0, 0.7, 15.7, 16.35);
        fade(waveP, 0.0, 0.7, 15.7, 16.35);
        var bx1 = addArrow(comp, "SIGMA_X_LEFT", [520, 420], [880, 420], C.blue, 4);
        var bx2 = addArrow(comp, "SIGMA_X_RIGHT", [1400, 420], [1040, 420], C.blue, 4);
        var bp1 = addArrow(comp, "SIGMA_P_LEFT", [640, 930], [900, 930], C.red, 4);
        var bp2 = addArrow(comp, "SIGMA_P_RIGHT", [1280, 930], [1020, 930], C.red, 4);
        var sx = addText(comp, "SIGMA_X", "2σx", [960, 435], 34, C.blue, "center", FONT_MATH);
        var sp = addText(comp, "SIGMA_P", "2σp", [960, 945], 34, C.red, "center", FONT_MATH);
        var i;
        var xOuterL = [], xInnerL = [], xOuterR = [], xInnerR = [];
        var pOuterL = [], pInnerL = [], pOuterR = [], pInnerR = [];
        var labelX = [], labelP = [];
        for (i = 0; i < times.length; i++) {
            xOuterL.push([centers[i] - widthsX[i], 420]);
            xInnerL.push([centers[i] - widthsX[i] * 0.18, 420]);
            xOuterR.push([centers[i] + widthsX[i], 420]);
            xInnerR.push([centers[i] + widthsX[i] * 0.18, 420]);
            pOuterL.push([centers[i] - widthsP[i], 930]);
            pInnerL.push([centers[i] - widthsP[i] * 0.18, 930]);
            pOuterR.push([centers[i] + widthsP[i], 930]);
            pInnerR.push([centers[i] + widthsP[i] * 0.18, 930]);
            labelX.push([centers[i], 435]);
            labelP.push([centers[i], 945]);
        }
        animateArrowPaths(bx1, times, xOuterL, xInnerL);
        animateArrowPaths(bx2, times, xOuterR, xInnerR);
        animateArrowPaths(bp1, times, pOuterL, pInnerL);
        animateArrowPaths(bp2, times, pOuterR, pInnerR);
        setKeys(tf(sx, "ADBE Position"), times, labelX, true);
        setKeys(tf(sp, "ADBE Position"), times, labelP, true);
        var allArrows = [bx1[0], bx1[1], bx2[0], bx2[1], bp1[0], bp1[1], bp2[0], bp2[1], sx, sp];
        for (i = 0; i < allArrows.length; i++) fade(allArrows[i], 0.7, 1.3, 15.4, 16.2);
        for (i = 0; i < 28; i++) {
            var dot = addCircle(comp, "P_SAMPLE_" + (i + 1), [960, 790], 20 + (i % 3) * 6, i % 2 === 0 ? C.red : C.blue, 34, null, 0);
            tf(dot, "ADBE Position").expression = "posterizeTime(60); seedRandom(Math.floor(time*60)+index*97,true); var w=150+300*(0.5+0.5*Math.sin(time*0.9)); var g=0; for(var k=0;k<6;k++) g+=random(); g-=3; [960+g*w/3,790];";
            tf(dot, "ADBE Opacity").expression = "posterizeTime(30); seedRandom(Math.floor(time*30)+index*23,true); random(20,50);";
        }
        var oneD = addText(comp, "ONE_DIMENSION_NOTE", "一维：所有采样始终位于同一直线", [960, 1025], 26, C.gray, "center", FONT_CN);
        fade(oneD, 1.0, 1.6, 15.5, 16.2);
        return comp;
    }

    function buildWavefunction(sceneFolder) {
        var comp = makeComp("S03_WAVEFUNCTION_AE_12_7s", 762, sceneFolder);
        var axis = addPath(comp, "WAVE_AXIS", [[100, 555], [1820, 555]], C.gray, 3, false, null, 0).layer;
        fade(axis, 0.0, 0.5, 12.1, 12.65);
        var times = [0, 2.1, 4.2, 6.3, 8.5, 10.6, 12.7];
        var centers = [540, 720, 900, 1080, 1260, 1420, 1540];
        var sigmas = [300, 300, 300, 300, 300, 300, 300];
        var amps = [125, 125, 125, 125, 125, 125, 125];
        var cycles = [70, 70, 70, 70, 70, 70, 70];
        var re = addGaussianWaveLayer(comp, "RE_PSI", C.red, 5, 555, times, centers, sigmas, amps, cycles, [0, 1, 2, 3, 4, 5, 6], false);
        var im = addGaussianWaveLayer(comp, "IM_PSI", C.blue, 5, 555, times, centers, sigmas, amps, cycles, [1.57, 2.57, 3.57, 4.57, 5.57, 6.57, 7.57], false);
        var prob = addGaussianWaveLayer(comp, "ABS_PSI_SQUARED", C.cyan, 7, 555, times, centers, sigmas, [220, 220, 220, 220, 220, 220, 220], cycles, [0, 0, 0, 0, 0, 0, 0], true);
        setKeys(tf(prob, "ADBE Opacity"), [0, 2.2, 3.2, 6.6, 7.2], [0, 0, 100, 100, 0], true);
        var reLabel = addText(comp, "RE_LABEL", "Re ψ", [420, 780], 38, C.red, "center", FONT_MATH);
        var imLabel = addText(comp, "IM_LABEL", "Im ψ", [650, 780], 38, C.blue, "center", FONT_MATH);
        var probLabel = addText(comp, "PROB_LABEL", "|ψ|²", [960, 305], 44, C.cyan, "center", FONT_MATH);
        fade(reLabel, 0.3, 0.8, 6.5, 7.1);
        fade(imLabel, 0.3, 0.8, 6.5, 7.1);
        setKeys(tf(probLabel, "ADBE Opacity"), [0, 2.2, 3.2, 6.5, 7.1], [0, 0, 100, 100, 0], true);
        var relation = addText(comp, "PROB_RELATION", "|ψ(x,t)|²  =  (Re ψ)²  +  (Im ψ)²", [960, 180], 52, C.white, "center", FONT_MATH);
        setKeys(tf(relation, "ADBE Opacity"), [0, 2.3, 3.1, 6.3, 6.9], [0, 0, 100, 100, 0], true);
        var sch = addText(comp, "SCHRODINGER", "− ℏ²/(2m) · d²ψ/dx²  +  V(x)ψ  =  Eψ", [960, 205], 56, C.white, "center", FONT_MATH);
        setKeys(tf(sch, "ADBE Opacity"), [0, 6.5, 7.2, 12.0, 12.6], [0, 0, 100, 100, 0], true);
        var vMark = addText(comp, "V_HIGHLIGHT", "V(x)", [980, 290], 54, C.orange, "center", FONT_MATH);
        setKeys(tf(vMark, "ADBE Opacity"), [0, 7.1, 7.8, 12.0, 12.6], [0, 0, 100, 100, 0], true);
        var well = addPath(comp, "POTENTIAL_WELL", [[260, 760], [260, 540], [520, 540], [520, 760]], C.blue, 5, false, null, 0).layer;
        var free = addPath(comp, "POTENTIAL_FREE", [[730, 650], [1030, 650]], C.cyan, 5, false, null, 0).layer;
        var oscPts = [];
        var i;
        for (i = 0; i <= 80; i++) {
            var ox = 1250 + i * 5;
            var oy = 760 - 0.0045 * (ox - 1450) * (ox - 1450);
            oscPts.push([ox, oy]);
        }
        var osc = addPath(comp, "POTENTIAL_OSCILLATOR", oscPts, C.purple, 5, false, null, 0).layer;
        var wl = addText(comp, "WELL_LABEL", "势阱", [390, 835], 30, C.blue, "center", FONT_CN_BOLD);
        var fl = addText(comp, "FREE_LABEL", "自由", [880, 835], 30, C.cyan, "center", FONT_CN_BOLD);
        var ol = addText(comp, "OSC_LABEL", "谐振", [1450, 835], 30, C.purple, "center", FONT_CN_BOLD);
        var icons = [well, free, osc, wl, fl, ol];
        for (i = 0; i < icons.length; i++) setKeys(tf(icons[i], "ADBE Opacity"), [0, 7.7, 8.3, 10.8, 11.4], [0, 0, 100, 100, 0], true);
        var barrier = addRect(comp, "POTENTIAL_RECT_BARRIER", [960, 700], [300, 300], C.orange, 18, C.orange, 5, 0).layer;
        setKeys(tf(barrier, "ADBE Opacity"), [0, 10.6, 11.4, 12.7], [0, 0, 100, 100], true);
        var bFormula = addText(comp, "BARRIER_FORMULA", "V(x)=V₀   (0<x<W)", [960, 905], 42, C.orange, "center", FONT_MATH);
        setKeys(tf(bFormula, "ADBE Opacity"), [0, 10.8, 11.5, 12.7], [0, 0, 100, 100], true);
        return comp;
    }

    function buildBarrierBridge(sceneFolder, blenderItem) {
        var comp = makeComp("S04_BARRIER_BRIDGE_AE_8_433s", 506, sceneFolder);
        var sch = addText(comp, "BRIDGE_FORMULA", "− ℏ²/(2m) · d²ψ/dx²  +  V(x)ψ  =  Eψ", [960, 150], 50, C.white, "center", FONT_MATH);
        fade(sch, 0, 0.5, 7.5, 8.3);
        var barrierObj = addRect(comp, "RECTANGULAR_BARRIER", [760, 550], [360, 460], C.orange, 18, C.orange, 6, 0);
        setKeys(tf(barrierObj.layer, "ADBE Scale"), [0, 1.2, 6.8, 7.7], [[30, 30], [100, 100], [100, 100], [70, 70]], true);
        setKeys(tf(barrierObj.layer, "ADBE Position"), [0, 1.2, 6.8, 7.7], [[960, 550], [760, 550], [760, 550], [1040, 540]], true);
        var wA = addArrow(comp, "W_ARROW_L", [580, 830], [745, 830], C.purple, 5);
        var wB = addArrow(comp, "W_ARROW_R", [940, 830], [775, 830], C.purple, 5);
        var vA = addArrow(comp, "V0_ARROW", [1010, 780], [1010, 330], C.orange, 5);
        var wText = addText(comp, "W_SYMBOL", "W", [760, 900], 46, C.purple, "center", FONT_MATH);
        var vText = addText(comp, "V0_SYMBOL", "V₀", [1080, 550], 46, C.orange, "center", FONT_MATH);
        var arrows = [wA[0], wA[1], wB[0], wB[1], vA[0], vA[1], wText, vText];
        var i;
        for (i = 0; i < arrows.length; i++) setKeys(tf(arrows[i], "ADBE Opacity"), [0, 1.0, 1.7, 6.7, 7.4], [0, 0, 100, 100, 0], true);
        var exp = addText(comp, "T_FORMULA", "T  ≈  A · e⁻²κW", [1350, 470], 60, C.white, "center", FONT_MATH);
        var relation = addText(comp, "PARAM_RELATION", "W     V₀     T", [1350, 600], 46, C.yellow, "center", FONT_MATH);
        fade(exp, 2.0, 2.8, 6.7, 7.4);
        fade(relation, 3.0, 3.8, 6.7, 7.4);
        var blend = comp.layers.add(blenderItem);
        blend.name = "MATCH_TO_BLENDER_FIRST_FRAME";
        blend.startTime = 7.25;
        blend.inPoint = 7.25;
        blend.outPoint = comp.duration;
        setKeys(tf(blend, "ADBE Opacity"), [7.25, 8.2], [0, 100], true);
        return comp;
    }

    function buildProbabilityChartNative(assetFolder) {
        var csv = new File(ROOT + "/sync/probability_frames_v3.csv");
        if (!csv.exists || !csv.open("r")) throw new Error("Missing probability CSV: " + csv.fsName);
        var headers = csv.readln().split(",");
        var rows = [];
        var line, values, row, i, j;
        while (!csv.eof) {
            line = csv.readln();
            if (!line) continue;
            values = line.split(",");
            row = {};
            for (j = 0; j < headers.length; j++) row[headers[j]] = values[j];
            rows.push(row);
        }
        csv.close();

        var frames = 2937;
        var duration = frames / FPS;
        var c = app.project.items.addComp("PROBABILITY_CHART_NATIVE", 640, 1080, 1, duration, FPS);
        c.parentFolder = assetFolder;
        c.bgColor = C.bg;
        var bg = c.layers.addSolid(C.bg, "CHART_BG", 640, 1080, 1, duration);
        bg.moveToEnd();

        addText(c, "CHART_TITLE", "透射与反射概率", [52, 70], 34, C.white, "left", FONT_CN_BOLD);
        addText(c, "SUM_RULE", "T + R = 1", [585, 70], 24, C.yellow, "right", FONT_MATH);
        addText(c, "UPPER_LABEL", "概率", [52, 165], 25, C.white, "left", FONT_CN_BOLD);
        addText(c, "LOWER_LABEL", "log₁₀ 概率", [52, 605], 25, C.white, "left", FONT_CN_BOLD);

        addPath(c, "UPPER_AXIS_X", [[82, 500], [585, 500]], C.gray, 2, false, null, 0);
        addPath(c, "UPPER_AXIS_Y", [[82, 205], [82, 500]], C.gray, 2, false, null, 0);
        addPath(c, "LOWER_AXIS_X", [[82, 935], [585, 935]], C.gray, 2, false, null, 0);
        addPath(c, "LOWER_AXIS_Y", [[82, 650], [82, 935]], C.gray, 2, false, null, 0);
        addText(c, "P100", "100%", [70, 215], 18, C.gray, "right", FONT_MATH);
        addText(c, "P0", "0%", [70, 505], 18, C.gray, "right", FONT_MATH);
        addText(c, "LOG0", "10⁰", [70, 660], 18, C.gray, "right", FONT_MATH);
        addText(c, "LOG9", "10⁻⁹", [70, 940], 18, C.gray, "right", FONT_MATH);
        addText(c, "BEFORE_LABEL", "势垒前", [205, 545], 23, C.white, "center", FONT_CN_BOLD);
        addText(c, "AFTER_LABEL", "势垒后", [435, 545], 23, C.white, "center", FONT_CN_BOLD);
        addText(c, "BEFORE_LOG_LABEL", "势垒前", [205, 980], 23, C.white, "center", FONT_CN_BOLD);
        addText(c, "AFTER_LOG_LABEL", "势垒后", [435, 980], 23, C.white, "center", FONT_CN_BOLD);

        addRect(c, "LEGEND_BASE", [135, 125], [22, 8], C.cyan, 100, null, 0, 0);
        addText(c, "LEGEND_BASE_TEXT", "基准", [155, 132], 19, C.cyan, "left", FONT_CN);
        addRect(c, "LEGEND_W", [285, 125], [22, 8], C.purple, 100, null, 0, 0);
        addText(c, "LEGEND_W_TEXT", "W 变化", [305, 132], 19, C.purple, "left", FONT_CN);
        addRect(c, "LEGEND_V", [455, 125], [22, 8], C.orange, 100, null, 0, 0);
        addText(c, "LEGEND_V_TEXT", "V₀ 变化", [475, 132], 19, C.orange, "left", FONT_CN);

        var baseUpperBefore = addRect(c, "BASE_UPPER_BEFORE", [175, 499], [22, 2], C.cyan, 100, null, 0, 2);
        var widthUpperBefore = addRect(c, "WIDTH_UPPER_BEFORE", [205, 499], [22, 2], C.purple, 100, null, 0, 2);
        var heightUpperBefore = addRect(c, "HEIGHT_UPPER_BEFORE", [235, 499], [22, 2], C.orange, 100, null, 0, 2);
        var baseUpperAfter = addRect(c, "BASE_UPPER_AFTER", [405, 499], [22, 2], C.cyan, 100, null, 0, 2);
        var widthUpperAfter = addRect(c, "WIDTH_UPPER_AFTER", [435, 499], [22, 2], C.purple, 100, null, 0, 2);
        var heightUpperAfter = addRect(c, "HEIGHT_UPPER_AFTER", [465, 499], [22, 2], C.orange, 100, null, 0, 2);
        var baseLogBefore = addRect(c, "BASE_LOG_BEFORE", [175, 651], [22, 2], C.cyan, 100, null, 0, 2);
        var widthLogBefore = addRect(c, "WIDTH_LOG_BEFORE", [205, 651], [22, 2], C.purple, 100, null, 0, 2);
        var heightLogBefore = addRect(c, "HEIGHT_LOG_BEFORE", [235, 651], [22, 2], C.orange, 100, null, 0, 2);
        var baseLogAfter = addRect(c, "BASE_LOG_AFTER", [405, 651], [22, 2], C.cyan, 100, null, 0, 2);
        var widthLogAfter = addRect(c, "WIDTH_LOG_AFTER", [435, 651], [22, 2], C.purple, 100, null, 0, 2);
        var heightLogAfter = addRect(c, "HEIGHT_LOG_AFTER", [465, 651], [22, 2], C.orange, 100, null, 0, 2);

        var times = [], basePB = [], basePA = [], baseLB = [], baseLA = [];
        var widthPB = [], widthPA = [], widthLB = [], widthLA = [];
        var heightPB = [], heightPA = [], heightLB = [], heightLA = [];
        var stateText = [];
        var selectedWidthAfter = 0.0115992093;
        var selectedHeightAfter = 0.0252693046;
        for (i = 0; i < rows.length; i++) {
            var local = parseFloat(rows[i].manim_frame) / FPS;
            if (local >= duration) continue;
            var pb = parseFloat(rows[i].p_before);
            var pa = parseFloat(rows[i].p_after);
            var lb = parseFloat(rows[i].log10_before);
            var la = parseFloat(rows[i].log10_after);
            var cpb = parseFloat(rows[i].comparison_before);
            var cpa = parseFloat(rows[i].comparison_after);
            var group = rows[i].comparison_group;
            var wpb = cpb, wpa = cpa, hpb = cpb, hpa = cpa;
            if (group !== "width") {
                wpa = local >= 37 ? selectedWidthAfter : pa;
                wpb = 1 - wpa;
            }
            if (group !== "height") {
                hpa = local >= 37 ? selectedHeightAfter : pa;
                hpb = 1 - hpa;
            }
            times.push(local);
            basePB.push(pb); basePA.push(pa); baseLB.push(lb); baseLA.push(la);
            widthPB.push(wpb); widthPA.push(wpa); widthLB.push(Math.max(-9, Math.log(Math.max(wpb, 1e-9)) / Math.LN10)); widthLA.push(Math.max(-9, Math.log(Math.max(wpa, 1e-9)) / Math.LN10));
            heightPB.push(hpb); heightPA.push(hpa); heightLB.push(Math.max(-9, Math.log(Math.max(hpb, 1e-9)) / Math.LN10)); heightLA.push(Math.max(-9, Math.log(Math.max(hpa, 1e-9)) / Math.LN10));
            if (rows[i].segment === "width_study") stateText.push("W = " + parseFloat(rows[i].width_factor).toFixed(2) + " W     V₀ = V₀");
            else if (rows[i].segment === "height_study") stateText.push("W = W     V₀ = " + parseFloat(rows[i].height_factor).toFixed(2) + " V₀");
            else stateText.push("W = W     V₀ = V₀");
        }

        function keyUpper(bar, values, x) {
            var sizes = [], positions = [], k;
            for (k = 0; k < values.length; k++) {
                var h = Math.max(2, Math.min(1, values[k]) * 285);
                sizes.push([22, h]);
                positions.push([x, 500 - h / 2]);
            }
            setSampledKeys(bar.size, times, sizes);
            setSampledKeys(bar.position, times, positions);
        }
        function keyLog(bar, values, x) {
            var sizes = [], positions = [], k;
            for (k = 0; k < values.length; k++) {
                var v = Math.max(-9, Math.min(0, values[k]));
                var h = Math.max(2, (-v / 9) * 285);
                sizes.push([22, h]);
                positions.push([x, 650 + h / 2]);
            }
            setSampledKeys(bar.size, times, sizes);
            setSampledKeys(bar.position, times, positions);
        }
        keyUpper(baseUpperBefore, basePB, 175); keyUpper(baseUpperAfter, basePA, 405);
        keyUpper(widthUpperBefore, widthPB, 205); keyUpper(widthUpperAfter, widthPA, 435);
        keyUpper(heightUpperBefore, heightPB, 235); keyUpper(heightUpperAfter, heightPA, 465);
        keyLog(baseLogBefore, baseLB, 175); keyLog(baseLogAfter, baseLA, 405);
        keyLog(widthLogBefore, widthLB, 205); keyLog(widthLogAfter, widthLA, 435);
        keyLog(heightLogBefore, heightLB, 235); keyLog(heightLogAfter, heightLA, 465);

        var widthBars = [widthUpperBefore.layer, widthUpperAfter.layer, widthLogBefore.layer, widthLogAfter.layer];
        var heightBars = [heightUpperBefore.layer, heightUpperAfter.layer, heightLogBefore.layer, heightLogAfter.layer];
        for (i = 0; i < widthBars.length; i++) setKeys(tf(widthBars[i], "ADBE Opacity"), [0, 27.9, 28.4, duration], [0, 0, 100, 100], true);
        for (i = 0; i < heightBars.length; i++) setKeys(tf(heightBars[i], "ADBE Opacity"), [0, 36.9, 37.4, duration], [0, 0, 100, 100], true);
        var state = addText(c, "PARAMETER_STATE", "W = W     V₀ = V₀", [320, 1035], 23, C.white, "center", FONT_MATH);
        setTextKeys(state, times, stateText);
        var formula = addText(c, "TRANSMISSION_FORMULA", "T ≈ A · e⁻²κW", [320, 590], 30, C.white, "center", FONT_MATH);
        setKeys(tf(formula, "ADBE Opacity"), [0, 24.5, 25.2, duration], [0, 0, 100, 100], true);
        return c;
    }

    function buildTunnelling(sceneFolder, blenderItem, probabilityItem) {
        var comp = makeComp("S05_TUNNELLING_AE_64_417s", 3865, sceneFolder);
        var blender = comp.layers.add(blenderItem);
        blender.name = "BLENDER_V3_CORE";
        blender.startTime = 0;
        blender.inPoint = 0;
        blender.outPoint = comp.duration;
        setKeys(tf(blender, "ADBE Scale"), [0, 9.4, 10.2, 58.6, 59.4, comp.duration], [[100, 100], [100, 100], [66.6667, 66.6667], [66.6667, 66.6667], [100, 100], [100, 100]], true);
        setKeys(tf(blender, "ADBE Position"), [0, 9.4, 10.2, 58.6, 59.4, comp.duration], [[960, 540], [960, 540], [640, 540], [640, 540], [960, 540], [960, 540]], true);
        var overlay = comp.layers.add(probabilityItem);
        overlay.name = "PROBABILITY_OVERLAY_SYNC";
        overlay.startTime = 10.0;
        overlay.inPoint = 10.0;
        overlay.outPoint = Math.min(comp.duration, 10.0 + probabilityItem.duration);
        tf(overlay, "ADBE Position").setValue([1600, 540]);
        tf(overlay, "ADBE Scale").setValue([100, 100]);
        setKeys(tf(overlay, "ADBE Opacity"), [10.0, 10.45, overlay.outPoint - 0.45, overlay.outPoint], [0, 100, 100, 0], true);
        var seam = addPath(comp, "LAYOUT_SEAM_ACCENT", [[1280, 90], [1280, 990]], C.blue, 2, false, null, 0).layer;
        setKeys(tf(seam, "ADBE Opacity"), [0, 10.0, 10.45, 58.6, 59.1], [0, 0, 28, 28, 0], true);
        var wTag = addText(comp, "SYNC_W", "W", [1260, 930], 34, C.purple, "right", FONT_MATH);
        var vTag = addText(comp, "SYNC_V0", "V₀", [1310, 930], 34, C.orange, "left", FONT_MATH);
        setKeys(tf(wTag, "ADBE Opacity"), [0, 10.2, 10.8, 58.3, 59.0], [0, 0, 100, 100, 0], true);
        setKeys(tf(vTag, "ADBE Opacity"), [0, 10.2, 10.8, 58.3, 59.0], [0, 0, 100, 100, 0], true);
        return comp;
    }

    function buildNandIcon(assetFolder) {
        var c = app.project.items.addComp("ICON_NAND_NATIVE", 900, 500, 1, 5, FPS);
        c.parentFolder = assetFolder;
        var oxide = addRect(c, "OXIDE", [450, 285], [560, 52], C.gray, 20, C.gray, 3, 0).layer;
        var gate = addRect(c, "CONTROL_GATE", [450, 120], [520, 90], C.blue, 28, C.blue, 4, 0).layer;
        var floating = addRect(c, "FLOATING_GATE", [450, 210], [360, 72], C.purple, 26, C.purple, 4, 0).layer;
        var substrate = addRect(c, "SUBSTRATE", [450, 390], [680, 95], C.orange, 16, C.orange, 4, 0).layer;
        var e = addCircle(c, "ELECTRON", [180, 390], 26, C.blue, 100, C.white, 2);
        setKeys(tf(e, "ADBE Position"), [0.2, 1.4, 2.7, 4.2], [[180, 390], [390, 390], [450, 230], [650, 230]], true);
        var minus = addText(c, "E_MINUS", "−", [180, 400], 28, C.white, "center", FONT_MATH);
        setKeys(tf(minus, "ADBE Position"), [0.2, 1.4, 2.7, 4.2], [[180, 400], [390, 400], [450, 240], [650, 240]], true);
        addText(c, "NAND_LABEL", "NAND", [450, 480], 42, C.white, "center", FONT_CN_BOLD);
        return c;
    }

    function buildStmIcon(assetFolder) {
        var c = app.project.items.addComp("ICON_STM_NATIVE", 900, 500, 1, 5, FPS);
        c.parentFolder = assetFolder;
        var i;
        for (i = 0; i < 9; i++) addCircle(c, "ATOM_" + i, [130 + i * 80, 380], 48, C.blue, 45, C.blue, 3);
        var probe = addPath(c, "STM_PROBE", [[420, 60], [480, 60], [455, 290], [445, 290]], C.white, 4, true, C.gray, 45).layer;
        setKeys(tf(probe, "ADBE Position"), [0, 2.5, 5], [[-180, 0], [0, 0], [180, 0]], true);
        var tunnel = addPath(c, "TUNNEL_CURRENT", [[450, 300], [430, 320], [470, 340], [435, 360], [465, 378]], C.cyan, 5, false, null, 0).layer;
        setKeys(tf(tunnel, "ADBE Opacity"), [0, 0.8, 1.1, 2.0, 2.3, 3.2, 3.5, 4.6], [10, 10, 100, 20, 100, 20, 100, 20], true);
        addText(c, "STM_LABEL", "STM", [450, 480], 42, C.white, "center", FONT_CN_BOLD);
        return c;
    }

    function buildCmosIcon(assetFolder) {
        var c = app.project.items.addComp("ICON_CMOS_NATIVE", 900, 500, 1, 5, FPS);
        c.parentFolder = assetFolder;
        addRect(c, "BODY", [450, 335], [620, 150], C.blue, 12, C.blue, 3, 0);
        addRect(c, "GATE", [450, 185], [160, 160], C.purple, 30, C.purple, 4, 0);
        addRect(c, "SOURCE", [250, 335], [150, 95], C.cyan, 30, C.cyan, 3, 0);
        addRect(c, "DRAIN", [650, 335], [150, 95], C.orange, 30, C.orange, 3, 0);
        addText(c, "S", "S", [250, 350], 36, C.white, "center", FONT_MATH);
        addText(c, "G", "G", [450, 200], 36, C.white, "center", FONT_MATH);
        addText(c, "D", "D", [650, 350], 36, C.white, "center", FONT_MATH);
        var leak = addArrow(c, "LEAKAGE", [310, 250], [590, 250], C.red, 6);
        setKeys(tf(leak[0], "ADBE Opacity"), [0, 1.0, 1.4, 4.5, 5.0], [0, 0, 100, 100, 0], true);
        setKeys(tf(leak[1], "ADBE Opacity"), [0, 1.0, 1.4, 4.5, 5.0], [0, 0, 100, 100, 0], true);
        var heat = addCircle(c, "HEAT", [450, 270], 360, C.red, 12, null, 0);
        addBlur(heat, 55);
        setKeys(tf(heat, "ADBE Scale"), [0, 1.2, 3.0, 5.0], [[30, 30], [50, 50], [120, 120], [80, 80]], true);
        addText(c, "CMOS_LABEL", "CMOS", [450, 480], 42, C.white, "center", FONT_CN_BOLD);
        return c;
    }

    function buildTunnelIcon(assetFolder) {
        var c = app.project.items.addComp("ICON_TUNNELLING_NATIVE", 900, 500, 1, 5, FPS);
        c.parentFolder = assetFolder;
        addPath(c, "AXIS", [[90, 300], [810, 300]], C.gray, 3, false, null, 0);
        addRect(c, "BARRIER", [450, 260], [100, 300], C.orange, 18, C.orange, 4, 0);
        var p = addCircle(c, "PARTICLE", [160, 300], 34, C.blue, 100, C.white, 2);
        setKeys(tf(p, "ADBE Position"), [0, 1.7, 2.3, 4.5], [[160, 300], [380, 300], [520, 300], [760, 300]], true);
        addGaussianWaveLayer(c, "PROBABILITY", C.cyan, 5, 300, [0, 2.2, 5], [240, 450, 680], [170, 120, 130], [90, 65, 72], [60, 50, 55], [0, 2, 4], false);
        addText(c, "TUNNEL_LABEL", "量子隧穿", [450, 475], 42, C.white, "center", FONT_CN_BOLD);
        return c;
    }

    function buildApplications(sceneFolder, assetFolder) {
        var comp = makeComp("S06_APPLICATIONS_AE_23_033s", 1382, sceneFolder);
        var tunnelComp = buildTunnelIcon(assetFolder);
        var nandComp = buildNandIcon(assetFolder);
        var stmComp = buildStmIcon(assetFolder);
        var cmosComp = buildCmosIcon(assetFolder);
        var tunnel = comp.layers.add(tunnelComp);
        tunnel.name = "MAIN_TUNNELLING";
        tf(tunnel, "ADBE Position").setValue([340, 210]);
        tf(tunnel, "ADBE Scale").setValue([42, 42]);
        tf(tunnel, "ADBE Opacity").setValue(45);
        var nand = comp.layers.add(nandComp);
        nand.name = "APPLICATION_NAND";
        var stm = comp.layers.add(stmComp);
        stm.name = "APPLICATION_STM";
        var cmos = comp.layers.add(cmosComp);
        cmos.name = "APPLICATION_CMOS";
        setLayerTimeMap(nand, [0, 1.8, 4.8, 23.033], [0, 0, 3.0, 3.0], comp.duration);
        setLayerTimeMap(stm, [0, 7.2, 10.2, 23.033], [0, 0, 3.0, 3.0], comp.duration);
        setLayerTimeMap(cmos, [0, 12.2, 15.2, 23.033], [0, 0, 3.0, 3.0], comp.duration);
        setLayerTimeMap(tunnel, [0, 17.0, 22.0, 23.033], [2.5, 0, 4.95, 4.95], comp.duration);
        setKeys(tf(nand, "ADBE Position"), [0, 1.8, 5.5, 6.7, 23.033], [[410, 820], [960, 535], [960, 535], [370, 800], [370, 800]], true);
        setKeys(tf(nand, "ADBE Scale"), [0, 1.8, 5.5, 6.7, 23.033], [[48, 48], [100, 100], [100, 100], [50, 50], [50, 50]], true);
        setKeys(tf(nand, "ADBE Opacity"), [0, 1.5, 1.8, 5.5, 6.7, 7.0, 17.0, 17.4], [22, 22, 100, 100, 20, 35, 35, 100], true);
        setKeys(tf(stm, "ADBE Position"), [0, 6.7, 7.2, 10.8, 12.0, 23.033], [[960, 800], [960, 800], [960, 535], [960, 535], [960, 800], [960, 800]], true);
        setKeys(tf(stm, "ADBE Scale"), [0, 6.7, 7.2, 10.8, 12.0, 23.033], [[50, 50], [50, 50], [100, 100], [100, 100], [50, 50], [50, 50]], true);
        setKeys(tf(stm, "ADBE Opacity"), [0, 6.7, 7.2, 10.8, 12.0, 12.3, 17.0, 17.4], [22, 22, 100, 100, 100, 35, 35, 100], true);
        setKeys(tf(cmos, "ADBE Position"), [0, 11.8, 12.2, 16.0, 17.2, 23.033], [[1510, 800], [1510, 800], [960, 535], [960, 535], [1550, 800], [1550, 800]], true);
        setKeys(tf(cmos, "ADBE Scale"), [0, 11.8, 12.2, 16.0, 17.2, 23.033], [[50, 50], [50, 50], [100, 100], [100, 100], [50, 50], [50, 50]], true);
        setKeys(tf(cmos, "ADBE Opacity"), [0, 11.8, 12.2, 16.0, 17.2], [22, 22, 100, 100, 100], true);
        setKeys(tf(tunnel, "ADBE Position"), [0, 17.0, 19.0, 23.033], [[340, 210], [340, 210], [960, 235], [960, 235]], true);
        setKeys(tf(tunnel, "ADBE Scale"), [0, 17.0, 19.0, 23.033], [[42, 42], [42, 42], [70, 70], [70, 70]], true);
        setKeys(tf(tunnel, "ADBE Opacity"), [0, 16.8, 17.4, 23.033], [45, 45, 100, 100], true);
        var a1 = addArrow(comp, "RELATION_NAND", [830, 390], [470, 670], C.orange, 4);
        var a2 = addArrow(comp, "RELATION_STM", [960, 400], [960, 665], C.blue, 4);
        var a3 = addArrow(comp, "RELATION_CMOS", [1090, 390], [1450, 670], C.red, 4);
        var arr = [a1[0], a1[1], a2[0], a2[1], a3[0], a3[1]];
        var i;
        for (i = 0; i < arr.length; i++) setKeys(tf(arr[i], "ADBE Opacity"), [0, 18.8, 20.8, 23.033], [0, 0, 100, 100], true);
        return comp;
    }

    function buildCredits(sceneFolder) {
        var comp = makeComp("S07_CREDITS_AE_5_5s", 330, sceneFolder);
        var title = addText(comp, "CREDITS_TITLE", "参考与延伸", [180, 150], 62, C.white, "left", FONT_CN_BOLD);
        fade(title, 0, 0.5, 4.7, 5.4);
        var line = addPath(comp, "CREDITS_LINE", [[180, 205], [1680, 205]], C.blue, 3, false, null, 0).layer;
        fade(line, 0.1, 0.8, 4.7, 5.4);
        var book = addText(comp, "REF_BOOK", "量子力学概论    David J. Griffiths", [180, 330], 36, C.white, "left", FONT_CN);
        var phet = addText(comp, "REF_PHET", "量子隧穿与波包    phet.colorado.edu/zh_CN/simulations/quantum-tunneling", [180, 455], 32, C.blue, "left", FONT_CN);
        var github = addText(comp, "REF_GITHUB", "开源演示    github.com/louishrm/Quantum-Tunneling", [180, 580], 32, C.green, "left", FONT_CN);
        var thanks = addText(comp, "THANKS", "极小的概率，也能成为现实。", [960, 850], 46, C.yellow, "center", FONT_CN_BOLD);
        var credits = [book, phet, github, thanks];
        var i;
        for (i = 0; i < credits.length; i++) fade(credits[i], 0.4 + i * 0.25, 1.1 + i * 0.25, 4.7, 5.4);
        return comp;
    }

    function addMasterLayer(master, comp, startFrame) {
        var l = master.layers.add(comp);
        l.name = comp.name;
        l.startTime = startFrame / FPS;
        l.inPoint = startFrame / FPS;
        l.outPoint = (startFrame + Math.round(comp.duration * FPS)) / FPS;
        return l;
    }

    function buildMaster(masterFolder, scenes, footageFolder) {
        var master = makeComp("MASTER_AE_RECONSTRUCTION_179_5s", 10770, masterFolder);
        var starts = [0, 2940, 3925, 4687, 5193, 9058, 10440];
        var i;
        for (i = 0; i < scenes.length; i++) addMasterLayer(master, scenes[i], starts[i]);
        var chapters = [
            [0, "01 核聚变与经典矛盾"],
            [2940, "02 不确定性原理"],
            [3925, "03 波函数语言"],
            [4687, "04 势垒模型"],
            [5193, "05 量子隧穿演示"],
            [9058, "06 现实应用"],
            [10440, "07 参考与结语"]
        ];
        for (i = 0; i < chapters.length; i++) addReferenceMarker(master, chapters[i][0] / FPS, chapters[i][1]);
        var vo = [
            [0, "VO01 核聚变，是我们从高中物理就熟悉的概念。"],
            [408, "VO02 太阳已燃烧约四十六亿年。"],
            [828, "VO03 经典估算带来矛盾。"],
            [1290, "VO04 经典阈值远高于太阳核心温度。"],
            [1752, "VO05 经典图景下原子核会被弹回。"],
            [2232, "VO06 经典理论漏掉了什么？"],
            [2736, "VO07 答案，是量子隧穿。"],
            [2940, "VO08 位置与动量不能同时任意压缩。"],
            [3432, "VO09 这是量子态本身的结构。"],
            [3925, "VO10 电子不能只被看作确定轨迹小球。"],
            [4308, "VO11 波函数模方是概率密度。"],
            [4687, "VO12 势能函数V编码环境。"],
            [5193, "VO13 局域波包接近矩形势垒。"],
            [5724, "VO14 量子结果与经典图景不同。"],
            [6270, "VO15 波函数及一阶导数在边界连续。"],
            [6840, "VO16 反射、透射与倏逝解。"],
            [7380, "VO17 分开的是概率流。"],
            [7910, "VO18 单次测量得到完整电子。"],
            [8418, "VO19 透射率对W与V0指数敏感。"],
            [9058, "VO20 NAND闪存。"],
            [9504, "VO21 扫描隧道显微镜。"],
            [9948, "VO22 器件泄漏与发热。"],
            [10440, "VO23 极小概率成为现实。"]
        ];
        for (i = 0; i < vo.length; i++) addReferenceMarker(master, vo[i][0] / FPS, vo[i][1]);
        return master;
    }

    app.beginUndoGroup("Build Quantum Tunnelling AE Reconstruction V1");
    try {
        try { app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES); } catch (closeError) {}
        app.newProject();
        var rootFolder = makeFolder("QT_AE_REBUILD_V1", null);
        var masterFolder = makeFolder("00_MASTER", rootFolder);
        var sceneFolder = makeFolder("01_SCENES", rootFolder);
        var assetFolder = makeFolder("02_NATIVE_ASSETS", rootFolder);
        var footageFolder = makeFolder("03_IMPORTED_MEDIA", rootFolder);
        var refFolder = makeFolder("04_REFERENCE_ONLY", rootFolder);

        var blender = importFootage(ROOT + "/resolve_edit/proxies/blender_v3_selected_animatic_1080p60.mp4", "BLENDER_V3_SELECTED_1080P60", footageFolder);
        importFootage(ROOT + "/resource/fromAI/10_review_proxies/probability_overlay_v3_html_640x1080p60.mp4", "REF_PROBABILITY_OVERLAY_V3", refFolder);
        importFootage(ROOT + "/resource/fromAI/10_review_proxies/fusion_quantum_bridge_v8_1080p60.mp4", "REF_FUSION_V8", refFolder);
        importFootage(ROOT + "/resource/fromAI/10_review_proxies/uncertainty_1d_stochastic_v3_1080p60.mp4", "REF_UNCERTAINTY_V3", refFolder);
        importFootage(ROOT + "/resolve_edit/proxies/wavefunction_language_edit_1080p60.mp4", "REF_WAVEFUNCTION_EDIT", refFolder);
        importFootage(ROOT + "/resolve_edit/proxies/blender_bridge_edit_1080p60.mp4", "REF_BARRIER_BRIDGE", refFolder);
        importFootage(ROOT + "/resource/fromAI/10_review_proxies/tunnelling_applications_intermediate_layout_v7_1080p60.mp4", "REF_APPLICATIONS_V7", refFolder);
        importFootage(ROOT + "/resolve_edit/proxies/credits_5_5s_1080p60.mp4", "REF_CREDITS", refFolder);

        var s1 = buildFusion(sceneFolder);
        var s2 = buildUncertainty(sceneFolder);
        var s3 = buildWavefunction(sceneFolder);
        var s4 = buildBarrierBridge(sceneFolder, blender);
        var probabilityNative = buildProbabilityChartNative(assetFolder);
        var s5 = buildTunnelling(sceneFolder, blender, probabilityNative);
        var s6 = buildApplications(sceneFolder, assetFolder);
        var s7 = buildCredits(sceneFolder);
        var master = buildMaster(masterFolder, [s1, s2, s3, s4, s5, s6, s7], footageFolder);

        master.openInViewer();
        app.project.save(new File(OUT_AEP));
        return "OK|" + OUT_AEP + "|items=" + app.project.numItems + "|masterFrames=" + Math.round(master.duration * FPS);
    } catch (error) {
        throw error;
    } finally {
        app.endUndoGroup();
    }
})();
