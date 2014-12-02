from numpy.linalg import norm

# numpy based operations for any dimension

def equal(vec1, vec2):
    return (vec1==vec2).all()

def dot(vec1, vec2):
    """ Calculate the dot product of two 3d vectors. """
    return vec1.dot(vec2)

def normalize(vec):
    """ Calculate the normalized vector (norm: one). """
    return vec / norm(vec)

def proj(u, v):
    factor = u.dot(v) / u.dot(u)
    return factor*u

def projfac(u, v):
    factor = u.dot(v) / u.dot(u)
    return factor

def cos_angle(p, q):
    """Calculate the cosine of angle between vector p and q
    see http://en.wikipedia.org/wiki/Law_of_cosines#Vector_formulation
    """
    return p.dot(q) / ( norm(p) * norm(q) )

def compute_radius(p, p_n, q):
    """compute radius of ball that touches points p and q and is centered on along the normal p_n of p. Numpy array inputs."""
    # this is basic goniometry
    d = norm(p-q)
    cos_theta = p_n.dot(p-q) / d
    return d/(2*cos_theta)
    