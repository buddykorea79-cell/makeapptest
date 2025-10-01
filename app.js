import { SUPABASE_URL, SUPABASE_ANON_KEY } from './config.js';
import { createClient } from 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js/+esm';

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

function logStatus(message, isError = false) {
    const chartContainer = document.getElementById('chart-container');
    const loadingMessage = document.getElementById('loading-message');

    if (loadingMessage) {
        loadingMessage.style.display = 'none';
    }

    const className = isError 
        ? "p-4 text-red-700 bg-red-100 border border-red-300 rounded-lg font-mono text-sm" 
        : "p-4 text-gray-700 bg-gray-100 border border-gray-300 rounded-lg text-sm";
    
    chartContainer.innerHTML = `<div class="${className}">${message}</div>` + chartContainer.innerHTML;
}

/**
 * 통계 정보 계산 함수
 */
function calculateStats(irisData) {
    const stats = {
        totalCount: irisData.length,
        speciesCounts: {},
        avgSepalLength: 0,
        avgPetalLength: 0,
        avgSepalWidth: 0,
        avgPetalWidth: 0
    };

    let sepalLengthSum = 0, petalLengthSum = 0;
    let sepalWidthSum = 0, petalWidthSum = 0;

    irisData.forEach(row => {
        const species = row.Species || 'Unknown';
        stats.speciesCounts[species] = (stats.speciesCounts[species] || 0) + 1;
        
        sepalLengthSum += row.SepalLengthCm || 0;
        petalLengthSum += row.PetalLengthCm || 0;
        sepalWidthSum += row.SepalWidthCm || 0;
        petalWidthSum += row.PetalWidthCm || 0;
    });

    stats.avgSepalLength = (sepalLengthSum / irisData.length).toFixed(2);
    stats.avgPetalLength = (petalLengthSum / irisData.length).toFixed(2);
    stats.avgSepalWidth = (sepalWidthSum / irisData.length).toFixed(2);
    stats.avgPetalWidth = (petalWidthSum / irisData.length).toFixed(2);

    return stats;
}

/**
 * 통계 카드 렌더링
 */
function renderStatsCards(stats) {
    const statsContainer = document.getElementById('stats-container');
    const speciesColors = {
        'Iris-setosa': 'bg-blue-500',
        'Iris-versicolor': 'bg-green-500',
        'Iris-virginica': 'bg-purple-500'
    };

    let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">';
    
    // 총 데이터 수
    html += `
        <div class="bg-gradient-to-br from-indigo-500 to-indigo-600 text-white p-6 rounded-xl shadow-lg">
            <h3 class="text-sm font-semibold opacity-90 mb-2">총 데이터</h3>
            <p class="text-4xl font-bold">${stats.totalCount}</p>
            <p class="text-xs mt-2 opacity-80">개의 샘플</p>
        </div>
    `;

    // 평균 꽃받침 길이
    html += `
        <div class="bg-gradient-to-br from-pink-500 to-pink-600 text-white p-6 rounded-xl shadow-lg">
            <h3 class="text-sm font-semibold opacity-90 mb-2">평균 꽃받침 길이</h3>
            <p class="text-4xl font-bold">${stats.avgSepalLength}</p>
            <p class="text-xs mt-2 opacity-80">cm</p>
        </div>
    `;

    // 평균 꽃잎 길이
    html += `
        <div class="bg-gradient-to-br from-emerald-500 to-emerald-600 text-white p-6 rounded-xl shadow-lg">
            <h3 class="text-sm font-semibold opacity-90 mb-2">평균 꽃잎 길이</h3>
            <p class="text-4xl font-bold">${stats.avgPetalLength}</p>
            <p class="text-xs mt-2 opacity-80">cm</p>
        </div>
    `;

    // 종 개수
    html += `
        <div class="bg-gradient-to-br from-amber-500 to-amber-600 text-white p-6 rounded-xl shadow-lg">
            <h3 class="text-sm font-semibold opacity-90 mb-2">총 종 개수</h3>
            <p class="text-4xl font-bold">${Object.keys(stats.speciesCounts).length}</p>
            <p class="text-xs mt-2 opacity-80">Species</p>
        </div>
    `;

    html += '</div>';
    statsContainer.innerHTML = html;
}

/**
 * 1. 산점도 매트릭스 (Scatter Matrix)
 */
function createScatterMatrix(irisData) {
    const dimensions = [
        { label: 'Sepal Length', values: irisData.map(d => d.SepalLengthCm) },
        { label: 'Sepal Width', values: irisData.map(d => d.SepalWidthCm) },
        { label: 'Petal Length', values: irisData.map(d => d.PetalLengthCm) },
        { label: 'Petal Width', values: irisData.map(d => d.PetalWidthCm) }
    ];

    const colors = irisData.map(d => {
        if (d.Species === 'Iris-setosa') return 0;
        if (d.Species === 'Iris-versicolor') return 1;
        return 2;
    });

    const trace = {
        type: 'splom',
        dimensions: dimensions,
        marker: {
            color: colors,
            colorscale: [[0, '#3B82F6'], [0.5, '#10B981'], [1, '#A855F7']],
            size: 5,
            line: { color: 'white', width: 0.5 }
        }
    };

    const layout = {
        title: '📊 산점도 매트릭스 (Scatter Plot Matrix)',
        height: 700,
        autosize: true,
        hovermode: 'closest',
        dragmode: 'select',
        plot_bgcolor: 'rgba(240,240,240,0.9)'
    };

    Plotly.newPlot('scatter-matrix', [trace], layout, { responsive: true });
}

/**
 * 2. 3D 산점도
 */
function create3DScatter(irisData) {
    const speciesGroups = {};
    const colors = {
        'Iris-setosa': '#3B82F6',
        'Iris-versicolor': '#10B981',
        'Iris-virginica': '#A855F7'
    };

    irisData.forEach(row => {
        const species = row.Species || 'Unknown';
        if (!speciesGroups[species]) {
            speciesGroups[species] = {
                x: [], y: [], z: [],
                mode: 'markers',
                type: 'scatter3d',
                name: species,
                marker: {
                    size: 5,
                    color: colors[species] || '#999',
                    opacity: 0.8,
                    line: { color: 'white', width: 0.5 }
                }
            };
        }
        speciesGroups[species].x.push(row.SepalLengthCm);
        speciesGroups[species].y.push(row.SepalWidthCm);
        speciesGroups[species].z.push(row.PetalLengthCm);
    });

    const layout = {
        title: '🌐 3D 산점도 (Sepal Length, Width, Petal Length)',
        scene: {
            xaxis: { title: 'Sepal Length (cm)' },
            yaxis: { title: 'Sepal Width (cm)' },
            zaxis: { title: 'Petal Length (cm)' },
            camera: {
                eye: { x: 1.5, y: 1.5, z: 1.3 }
            }
        },
        height: 600,
        autosize: true
    };

    Plotly.newPlot('scatter-3d', Object.values(speciesGroups), layout, { responsive: true });
}

/**
 * 3. 박스 플롯 (Box Plot)
 */
function createBoxPlots(irisData) {
    const species = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica'];
    const colors = ['#3B82F6', '#10B981', '#A855F7'];
    const measurements = ['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'];
    const labels = ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width'];

    const traces = [];

    species.forEach((sp, idx) => {
        measurements.forEach((measure, mIdx) => {
            const values = irisData
                .filter(d => d.Species === sp)
                .map(d => d[measure]);

            traces.push({
                y: values,
                type: 'box',
                name: sp,
                legendgroup: sp,
                showlegend: mIdx === 0,
                marker: { color: colors[idx] },
                boxmean: 'sd',
                xaxis: `x${mIdx + 1}`,
                yaxis: `y${mIdx + 1}`
            });
        });
    });

    const layout = {
        title: '📦 측정값별 분포 비교 (Box Plots)',
        grid: { rows: 2, columns: 2, pattern: 'independent' },
        height: 700,
        showlegend: true,
        autosize: true,
        annotations: labels.map((label, idx) => ({
            text: label,
            showarrow: false,
            x: 0.5,
            xref: `x${idx + 1} domain`,
            y: 1.1,
            yref: `y${idx + 1} domain`,
            xanchor: 'center',
            yanchor: 'bottom',
            font: { size: 14, color: '#333' }
        }))
    };

    Plotly.newPlot('box-plots', traces, layout, { responsive: true });
}

/**
 * 4. 바이올린 플롯 (Violin Plot)
 */
function createViolinPlot(irisData) {
    const species = ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica'];
    const colors = ['#3B82F6', '#10B981', '#A855F7'];

    const traces = species.map((sp, idx) => {
        const petalLengths = irisData
            .filter(d => d.Species === sp)
            .map(d => d.PetalLengthCm);

        return {
            type: 'violin',
            y: petalLengths,
            name: sp,
            box: { visible: true },
            meanline: { visible: true },
            marker: { color: colors[idx] },
            line: { color: colors[idx] }
        };
    });

    const layout = {
        title: '🎻 꽃잎 길이 분포 (Violin Plot)',
        yaxis: { title: 'Petal Length (cm)', zeroline: false },
        height: 500,
        autosize: true
    };

    Plotly.newPlot('violin-plot', traces, layout, { responsive: true });
}

/**
 * 5. 히트맵 (Correlation Heatmap)
 */
function createCorrelationHeatmap(irisData) {
    const features = ['SepalLengthCm', 'SepalWidthCm', 'PetalLengthCm', 'PetalWidthCm'];
    const labels = ['Sepal Length', 'Sepal Width', 'Petal Length', 'Petal Width'];
    
    // 상관계수 계산
    const correlationMatrix = [];
    features.forEach((f1) => {
        const row = [];
        features.forEach((f2) => {
            const values1 = irisData.map(d => d[f1]);
            const values2 = irisData.map(d => d[f2]);
            row.push(calculateCorrelation(values1, values2));
        });
        correlationMatrix.push(row);
    });

    const trace = {
        z: correlationMatrix,
        x: labels,
        y: labels,
        type: 'heatmap',
        colorscale: 'RdBu',
        zmid: 0,
        text: correlationMatrix.map(row => row.map(v => v.toFixed(2))),
        texttemplate: '%{text}',
        textfont: { size: 12 },
        colorbar: { title: 'Correlation' }
    };

    const layout = {
        title: '🔥 상관관계 히트맵 (Correlation Matrix)',
        height: 500,
        autosize: true,
        xaxis: { side: 'bottom' },
        yaxis: { autorange: 'reversed' }
    };

    Plotly.newPlot('heatmap', [trace], layout, { responsive: true });
}

/**
 * 상관계수 계산 함수
 */
function calculateCorrelation(x, y) {
    const n = x.length;
    const sum_x = x.reduce((a, b) => a + b, 0);
    const sum_y = y.reduce((a, b) => a + b, 0);
    const sum_xy = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
    const sum_x2 = x.reduce((sum, xi) => sum + xi * xi, 0);
    const sum_y2 = y.reduce((sum, yi) => sum + yi * yi, 0);

    const numerator = n * sum_xy - sum_x * sum_y;
    const denominator = Math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y));

    return denominator === 0 ? 0 : numerator / denominator;
}

/**
 * 6. 파이 차트 (Species Distribution)
 */
function createPieChart(irisData) {
    const speciesCounts = {};
    irisData.forEach(row => {
        const species = row.Species || 'Unknown';
        speciesCounts[species] = (speciesCounts[species] || 0) + 1;
    });

    const trace = {
        values: Object.values(speciesCounts),
        labels: Object.keys(speciesCounts),
        type: 'pie',
        hole: 0.4,
        marker: {
            colors: ['#3B82F6', '#10B981', '#A855F7']
        },
        textinfo: 'label+percent',
        textposition: 'outside',
        automargin: true
    };

    const layout = {
        title: '🥧 종별 데이터 분포',
        height: 500,
        autosize: true,
        showlegend: true
    };

    Plotly.newPlot('pie-chart', [trace], layout, { responsive: true });
}

/**
 * 메인 시각화 함수
 */
async function visualizeIrisData() {
    const chartContainer = document.getElementById('chart-container');
    const loadingMessage = document.getElementById('loading-message');
    
    if (loadingMessage) {
        loadingMessage.style.display = 'block';
    }
    
    if (SUPABASE_URL.includes('YOUR_') || SUPABASE_ANON_KEY.includes('YOUR_')) {
        const errorMessage = `
            <strong>[진단 실패: 1단계]</strong> config.js 파일에 Supabase 키가 설정되지 않았습니다.
            <br><br>
            <strong>조치 사항:</strong>
            <ol class="list-decimal list-inside ml-4 mt-2">
                <li>./config.js 파일을 열어 'YOUR_SUPABASE_URL_HERE'와 'YOUR_SUPABASE_ANON_KEY_HERE'를 실제 Supabase 키로 변경하세요.</li>
            </ol>
        `;
        chartContainer.innerHTML = `<div class="p-6 text-red-800 bg-red-200 border-2 border-red-500 rounded-xl">${errorMessage}</div>`;
        return;
    }

    logStatus('[진단 1단계 성공] Supabase 키 설정 확인 완료.');

    const { data: irisData, error } = await supabase
        .from('iris')
        .select('SepalLengthCm, SepalWidthCm, PetalLengthCm, PetalWidthCm, Species');

    if (loadingMessage) {
        loadingMessage.style.display = 'none';
    }

    if (error) {
        const errorMessage = `
            <div class="p-6 text-red-800 bg-red-200 border-2 border-red-500 rounded-xl">
                <h3 class="text-xl font-bold mb-3">데이터 로드 실패</h3>
                <p class="font-bold">Supabase 응답 오류:</p>
                <code class="block whitespace-pre-wrap bg-red-100 p-2 rounded">${JSON.stringify(error, null, 2)}</code>
            </div>
        `;
        chartContainer.innerHTML = errorMessage;
        console.error('Supabase 데이터 로드 중 오류 발생:', error);
        return;
    }

    logStatus(`[진단 2단계 성공] ${irisData.length}개의 데이터 레코드 로드 완료.`);
    
    // 통계 정보 표시
    const stats = calculateStats(irisData);
    renderStatsCards(stats);

    // 모든 차트 생성
    createScatterMatrix(irisData);
    create3DScatter(irisData);
    createBoxPlots(irisData);
    createViolinPlot(irisData);
    createCorrelationHeatmap(irisData);
    createPieChart(irisData);
}

window.onload = visualizeIrisData;
