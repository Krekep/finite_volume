def periodic_boundary_condition(domain: str, face_domain: int = 0, face_group: int = 0, value: int = 255):
    match domain:
        case "p":
            return p_periodic_boundary_condition(face_domain, face_group, 255)
        case "std":
            return std_periodic_boundary_condition(face_domain, face_group, 255)
        case "stdref":
            return std_periodic_boundary_condition(face_domain, face_group, 255)
        case "circle_eye":
            return circle_eye_periodic_boundary_condition(face_domain, face_group, 295)
        case "circle":
            return circle_periodic_boundary_condition(face_domain, face_group, 255)
        case "triangle":
            return triangle_periodic_boundary_condition(face_domain, face_group, 255)


def p_periodic_boundary_condition(face_domain: int, face_group: int, value: int) -> int:
    if face_domain == 0:
        return 0
    return value


def std_periodic_boundary_condition(face_domain: int, face_group: int, value: int) -> int:
    if face_group == 3:
        return value
    return 0


def circle_eye_periodic_boundary_condition(face_domain: int, face_group: int, value: int) -> int:
    if face_domain == 0:
        return value
    return 0


def circle_periodic_boundary_condition(face_domain: int, face_group: int, value: int) -> int:
    if face_domain == 0 and (face_group == 6 or face_group == 8):
        return value
    return 0


def triangle_periodic_boundary_condition(face_domain: int, face_group: int, value: int) -> int:
    if face_group == 5 or face_group == 1 or face_group == 7:
        return value
    return 0
