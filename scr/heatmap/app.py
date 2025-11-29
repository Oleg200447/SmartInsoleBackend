import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ============================================
# Функция загрузки OBJ
# ============================================

def load_obj_with_materials(path):
    vertices = []
    faces_by_mat = {"default": []}
    current_material = "default"

    with open(path, "r") as f:
        for line in f:
            if line.startswith("v "):
                parts = line.split()
                vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith("usemtl"):
                parts = line.split()
                current_material = parts[1] if len(parts) > 1 else "default"
                faces_by_mat.setdefault(current_material, [])
            elif line.startswith("f "):
                parts = line.split()
                tri = [int(p.split("/")[0]) - 1 for p in parts[1:]]
                if len(tri) == 3:
                    faces_by_mat[current_material].append(tri)
                elif len(tri) == 4:
                    faces_by_mat[current_material].append([tri[0], tri[1], tri[2]])
                    faces_by_mat[current_material].append([tri[0], tri[2], tri[3]])
    return np.array(vertices), faces_by_mat

# ============================================
# Загружаем OBJ с кэшем
# ============================================

obj_path = "foot1.obj"

@st.cache_data
def load_obj_cached(path):
    return load_obj_with_materials(path)

verts, faces_by_mat = load_obj_cached(obj_path)
x, y, z = verts[:, 0], verts[:, 1], verts[:, 2]

# ============================================
# Цветовая шкала давления
# ============================================

pressure_colors = [
    "rgb(0,255,0)",
    "rgb(51,255,0)",
    "rgb(102,255,0)",
    "rgb(153,255,0)",
    "rgb(204,255,0)",
    "rgb(255,255,0)",
    "rgb(255,204,0)",
    "rgb(255,153,0)",
    "rgb(255,102,0)",
    "rgb(255,0,0)"
]

def get_color_by_value(val):
    idx = min(val // 100, 9)  # индекс цвета от 0 до 9
    return pressure_colors[idx]

# ============================================
# Streamlit интерфейс
# ============================================

st.set_page_config(page_title="3D Viewer", layout="wide", page_icon="🦶")
st.sidebar.title("Настройка давления по областям")

target_materials = [f"Mat.00{i}" for i in range(1, 9)]
default_color = "rgb(252, 218, 191)"

# Инициализация session_state для слайдеров
for mat in target_materials:
    if mat not in st.session_state:
        st.session_state[mat] = 0

# Слайдеры для управления давлением
for mat in target_materials:
    st.session_state[mat] = st.sidebar.slider(
        f"{mat} (давление 0-999)",
        min_value=0,
        max_value=999,
        value=st.session_state[mat],
        step=1
    )

# ============================================
# Создание Mesh3D
# ============================================

meshes = []

for mat_name, face_list in faces_by_mat.items():
    faces = np.array(face_list)
    color = get_color_by_value(st.session_state.get(mat_name, 0)) if mat_name in target_materials else default_color

    meshes.append(
        go.Mesh3d(
            x=x,
            y=y,
            z=z,
            i=faces[:, 0],
            j=faces[:, 1],
            k=faces[:, 2],
            color=color,
            opacity=1.0,
            hoverinfo="skip",
            flatshading=False,
            name=mat_name,
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                specular=0.5,
                roughness=0.5,
                fresnel=0.2
            ),
            lightposition=dict(x=100, y=200, z=0)
        )
    )


# ============================================
# Создаём линии с подписями для каждого материала
# ============================================

annotation_traces = []

# Векторы направлений, куда каждая линия будет "выстреливать"
direction = {
    "Mat.001": np.array([-4, -2, 0]),
    "Mat.002": np.array([-4, -2, 0]),
    "Mat.003": np.array([-4, -2, -2]),
    "Mat.004": np.array([4, -2, 2]),
    "Mat.005": np.array([4, -2, 0]),
    "Mat.006": np.array([4, -2, 0]),
    "Mat.007": np.array([-4, -2, 0]),
    "Mat.008": np.array([4, -2, 0]),
}

for mat_name in target_materials:
    face_list = faces_by_mat.get(mat_name)
    if not face_list:
        continue

    face_arr = np.array(face_list)
    unique_verts = np.unique(face_arr.flatten())

    # Центр зоны
    cx = np.mean(x[unique_verts])
    cy = np.mean(y[unique_verts])
    cz = np.mean(z[unique_verts])

    val = st.session_state.get(mat_name, 0)

    # Направление линии
    offset = direction.get(mat_name, np.array([0, 10, 0]))

    lx = cx + offset[0]
    ly = cy + offset[1]
    lz = cz + offset[2]

    # Линия (без hover-подсветки)
    annotation_traces.append(
        go.Scatter3d(
            x=[cx, lx],
            y=[cy, ly],
            z=[cz, lz],
            mode="lines",
            line=dict(width=4, color="rgb(255,255,255)"),
            hoverinfo="skip",
            hovertemplate=None,
            showlegend=False
        )
    )

    # Текст (также без hover)
    annotation_traces.append(
        go.Scatter3d(
            x=[lx],
            y=[ly],
            z=[lz],
            mode="text",
            text=[f"{val}"],
            hoverinfo="skip",
            hovertemplate=None,
            textposition="top center",
            textfont=dict(size=14, color="white"),
            showlegend=False
        )
    )

# Добавляем в фигуру
meshes.extend(annotation_traces)

# ============================================
# Отображение фигуры
# ============================================

fig = go.Figure(data=meshes)
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, showspikes=False),
        yaxis=dict(visible=False, showspikes=False),
        zaxis=dict(visible=False, showspikes=False),
        bgcolor="rgb(15,15,15)",
        dragmode="orbit",
        camera=dict(
            eye=dict(x=0.0, y=-2.5, z=0.0),   # положение камеры
            center=dict(x=0, y=0, z=0),    # центр сцены
            up=dict(x=0.15, y=0, z=1)         # направление "вверх"
        )
    ),
    paper_bgcolor="rgb(15,15,15)",
    font=dict(color="white"),
    margin=dict(l=0, r=0, t=0, b=0)
)

st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
