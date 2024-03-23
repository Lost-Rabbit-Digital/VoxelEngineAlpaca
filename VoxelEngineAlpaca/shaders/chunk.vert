#version 330 core

layout (location = 0) in ivec3 in_position;
layout (location = 1) in int voxel_id;
layout (location = 2) in int face_id;
layout (location = 3) in int ao_id;

uniform mat4 m_proj;
uniform mat4 m_view;
uniform mat4 m_model;

out vec3 voxel_color;
out vec2 uv;
out float shading;

// Values for desired shading of each ambient occlusion identifer
const float ao_values[4] = float[4](0.1, 0.25, 0.5, 1.0);

const float face_shading[6] = float[6](
    1.0, 0.5, // Top / Bottom
    0.5, 0.8, // Right / Left
    0.5, 0.8 // Front / Back
);

const vec2 uv_coords[4] = vec2[4](
    vec2(0, 0), vec2(0, 1),
    vec2(1, 0), vec2(1, 1)
);

const int uv_indices[12] = int[12](
    // Texture coordinates indices for even-face vertices
    1, 0, 2, 1, 2, 3,
    // Texture coordinates indices for odd-face vertices
    3, 0, 2, 3, 1, 0
);


vec3 hash31(float p) {
    vec3 p3 = fract(vec3(p * 21.2) * vec3(0.1, 0.2, 0.3));
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.xxy + p3.yzz) * p3.zyx) + 0.05;
}


void main() {
    // By taking the remainder of gl_VertexID this will always get the ordinal number of the vertex
    int uv_index = gl_VertexID % 6  + (face_id & 1) * 6;
    uv = uv_coords[uv_indices[uv_index]];
    voxel_color = hash31(voxel_id);
    shading = face_shading[face_id] * ao_values[ao_id];
    gl_Position = m_proj * m_view * m_model * vec4(in_position, 1.0);
}